# runtime/capability_runtime.py
from runtime.base_runtime import BaseRuntime
from capabilities.capability_resolver import CapabilityResolver
from capabilities.input_resolver import InputResolver
from capabilities.input_validator import InputValidator
from capabilities.capability_state_store import CapabilityStateStore
from llms.llm import get_llm
from capabilities.registry import vector_db
import uuid

class CapabilityRuntime(BaseRuntime):
    def __init__(self, capability_registry, resource_manager, memory_manager, human_manager):
        super().__init__(
            registry=capability_registry,
            resource_manager=resource_manager,
            memory_manager=memory_manager,
            human_manager=human_manager
        )
        self.capability_resolver = CapabilityResolver(capability_registry, vector_db_client=vector_db)
        self.input_resolver = InputResolver(get_llm_factory=get_llm)
        self.input_validator = InputValidator()
        self.state_store = CapabilityStateStore()

    async def resolve(self, context):
        """
        Layer 1 & 2: Embedding-based ranking + LLM selection.
        Returns the winning capability name and packs extracted parameters into context.
        """
        capability_name, extracted_inputs = await self.capability_resolver.resolve(context)
        
        if isinstance(context, dict):
            context["_pre_extracted_inputs"] = extracted_inputs
        elif not isinstance(context, str):
            setattr(context, "_pre_extracted_inputs", extracted_inputs)
            
        return capability_name

    async def run(self, capability_name, context):
        # ─── SAFE CAPTURE: EXTRACT PROCESS ID ───
        process_id = None
        if isinstance(context, dict):
            process_id = context.get("process_id")
        elif hasattr(context, "process_id"):
            process_id = context.process_id
        
        if not process_id:
            process_id = str(uuid.uuid4())

        state = self.state_store.load(process_id)
        capability = self.registry.get(capability_name)

        # ─── SAFE CAPTURE: EXTRACT RAW QUERY TEXT ───
        raw_query = ""
        if isinstance(context, str):
            raw_query = context
        elif isinstance(context, dict):
            raw_query = context.get("query", "")
        elif hasattr(context, "query"):
            raw_query = context.query

        # ─── STEP 1: INITIALIZE STATE IF PROCESS IS NEW ───
        if state is None:
            pre_extracted = None
            
            # Safe checking sequence to catch pre-extracted dictionary attributes
            if isinstance(context, dict):
                pre_extracted = context.get("_pre_extracted_inputs")
            elif not isinstance(context, str) and hasattr(context, "_pre_extracted_inputs"):
                pre_extracted = context._pre_extracted_inputs

            if isinstance(pre_extracted, dict):
                # Optimization hit! Ensure it's explicitly a dictionary layout
                print(f"[OS KERNEL] Short-circuiting InputResolver. Using pre-extracted inputs: {pre_extracted}")
                resolved_inputs = pre_extracted
            else:
                # Fallback path if context structure lacks arguments map
                print(f"[OS KERNEL] Fallback: Resolving inputs from query string.")
                resolved_inputs = await self.input_resolver.resolve(
                    query=raw_query,
                    capability=capability,
                    context=context
                )

            # --- DEFENSIVE GUARD ---
            # If the resolver fallback returns something unexpected, force it to an empty dictionary
            if not isinstance(resolved_inputs, dict):
                print(f"[OS KERNEL WARNING] expected dict arguments, received {type(resolved_inputs)}. Correcting layout.")
                resolved_inputs = {}

            # Validate parameters safely
            missing_inputs = await self.input_validator.validate(
                capability=capability,
                inputs=resolved_inputs
            )

            state = {
                "query": raw_query,
                "capability": capability_name,
                "resolved_inputs": resolved_inputs,
                "missing_inputs": missing_inputs,
                "status": "running"
            }
            self.state_store.save(process_id, state)

        # ─── STEP 2: HANDLE SUSPENSION IF INPUTS ARE MISSING ───
        if state["missing_inputs"]:
            field = state["missing_inputs"][0]
            
            request = await self.human_manager.ask(
                process_id=process_id,
                question=f"Please provide '{field}'"
            )

            state["request_id"] = request.request_id
            state["status"] = "waiting"
            self.state_store.save(process_id, state)

            return {
                "status": "waiting",
                "request_id": request.request_id
            }

        # ─── STEP 3: EXECUTE CAPABILITY ONCE ALL INPUTS ARE MET ───
        # Ensure your target capability can safely digest the parameter structure
        result = await capability.execute(context=context, inputs=state["resolved_inputs"])
        
        state["result"] = result
        state["status"] = "completed"
        self.state_store.save(process_id, state)
        self.state_store.delete(process_id)

        return {
            "status": "completed",
            "result": result
        }

    async def resume(self, process_id, response, context):
        state = self.state_store.load(process_id)
        if state is None:
            raise ValueError(f"State not found for process '{process_id}'")

        capability = self.registry.get(state["capability"])
        current_target_field = state["missing_inputs"][0] if state["missing_inputs"] else "input"

        augmented_query = (
            f"{state['query']} "
            f"[System asked for {current_target_field}] "
            f"Human responded: {response}"
        )
        print(f"\n[OS KERNEL] Augmented Conversation History:\n'{augmented_query}'\n")

        newly_resolved = await self.input_resolver.resolve(
            query=augmented_query,
            capability=capability,
            context=context
        )

        if not isinstance(newly_resolved, dict):
            newly_resolved = {}

        if current_target_field in state["missing_inputs"] and current_target_field not in newly_resolved:
            newly_resolved[current_target_field] = response

        state["resolved_inputs"].update(newly_resolved)

        # Sync changes back to context objects if active
        for field, val in state["resolved_inputs"].items():
            if not isinstance(context, str):
                if hasattr(context, "set_input"):
                    context.set_input(field, val)
                elif isinstance(context, dict):
                    context[field] = val
                else:
                    setattr(context, field, val)

        state["missing_inputs"] = await self.input_validator.validate(
            capability=capability,
            inputs=state["resolved_inputs"]
        )
        
        state["status"] = "running"
        state["query"] = augmented_query
        self.state_store.save(process_id, state)
        
        return state