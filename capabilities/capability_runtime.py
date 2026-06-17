# runtime/capability_runtime.py
from runtime.base_runtime import BaseRuntime
from capabilities.capability_resolver import CapabilityResolver
from capabilities.capability_state_store import CapabilityStateStore
from llms.llm import get_llm
from capabilities.registry import vector_db
import json
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
        self.llm = get_llm()  # Central system LLM core instance
        self.state_store = CapabilityStateStore()

    async def resolve(self, context):
        """Layer 1 & 2: Embedding-based ranking + LLM selection."""
        capability_name, extracted_inputs = await self.capability_resolver.resolve(context)
        if isinstance(context, dict):
            context["_pre_extracted_inputs"] = extracted_inputs
        elif not isinstance(context, str):
            setattr(context, "_pre_extracted_inputs", extracted_inputs)
        return capability_name

    async def run(self, capability_name, context):
        """The core high-level OS execution loop orchestrator."""
        process_id = getattr(context, "process_id", None) or str(uuid.uuid4())
        state = self.state_store.load(process_id)
        capability = self.registry.get(capability_name)
        raw_query = context if isinstance(context, str) else getattr(context, "query", "")

        # ─── STEP 1: INITIALIZE STATE (IF BRAND NEW PROCESS) ───
        if state is None:
            state = await self._initialize_process_state(capability_name, capability, raw_query, context)
            self.state_store.save(process_id, state)

        # ─── STEP 2: HANDLE SUSPENSION (IF INPUT GAPS FOUND) ───
        if state["missing_inputs"]:
            return await self._handle_process_suspension(process_id, state)

        # ─── STEP 3: EXECUTE CAPABILITY TARGET ───
        result = await self._execute_sub_tool(capability, state, context)
        
        # Mark completed and purge the volatile state tracker
        state["result"] = result
        state["status"] = "completed"
        self.state_store.save(process_id, state)
        self.state_store.delete(process_id)

        return {
            "status": "completed",
            "result": result
        }

    # ------------------------------------------------------------------
    # MODULAR SUB-METHODS FOR CLEAN ARCHITECTURE
    # ------------------------------------------------------------------

    async def _initialize_process_state(self, capability_name: str, capability, raw_query: str, context) -> dict:
        """Extracts inputs, runs the dynamic micro-LLM router, and checks for missing variables."""
        pre_extracted = getattr(context, "_pre_extracted_inputs", None) or {}
        if not isinstance(pre_extracted, dict):
            pre_extracted = {}

        # 1. Dynamically identify the internal sub-tool path using the microkernel router
        target_sub_tool = await self._route_internal_sub_tool(capability_name, capability, raw_query, pre_extracted)

        # 2. Check for missing fields against the isolated sub-tool requirements
        missing_inputs = self._validate_sub_tool_inputs(capability, target_sub_tool, pre_extracted)

        return {
            "query": raw_query,
            "capability": capability_name,
            "sub_tool": target_sub_tool,
            "resolved_inputs": pre_extracted,
            "missing_inputs": missing_inputs,
            "status": "running"
        }

    async def _route_internal_sub_tool(self, capability_name: str, capability, raw_query: str, pre_extracted: dict) -> str:
            """Constructs a dynamic description prompt and executes a micro-token classification pass."""
            internal_tools = getattr(capability, "internal_tools", {})
            if not internal_tools:
                return capability_name  # Fallback for simple flat capability styles

            # Build an on-the-fly summary of available sub-actions from the manifest dictionary
            tool_manifest_summary = "".join(
                f"- '{t_name}': {t_config.get('description', '')}\n"
                for t_name, t_config in internal_tools.items()
            )

            micro_prompt = (
                f"You are the internal sub-routing microkernel for the '{capability_name}' suite.\n"
                f"User Raw Query: '{raw_query}'\n"
                f"Extracted Arguments: {json.dumps(pre_extracted)}\n\n"
                f"Available Internal Tools:\n{tool_manifest_summary}\n"
                f"Determine which specific internal tool name key must handle this task.\n"
                f"Pick exactly ONE matching name key from the options above.\n\n"
                f"CRITICAL: Output ONLY the raw string token key name (e.g., get_live_conditions). "
                f"No explanations, no markdown blocks, no trailing punctuation."
            )

            # ─── EXECUTE VIA YOUR NATIVE ASYNC WRAPPER ───
            # This safely runs the generation inside your background executor thread
            llm_result = await self.llm.ainvoke(micro_prompt)
            
            # Extract the content text string directly from your DummyLLMResult wrapper object
            response_text = llm_result.content
            
            return response_text.strip().replace("'", "").replace('"', "")
    
    
    def _validate_sub_tool_inputs(self, capability, sub_tool: str, resolved_inputs: dict) -> list:
        """Checks for missing required arguments purely based on the targeted sub-tool requirements."""
        internal_tools = getattr(capability, "internal_tools", {})
        chosen_tool_config = internal_tools.get(sub_tool, {})
        required_fields = chosen_tool_config.get("required_fields", [])

        missing_fields = []
        for field in required_fields:
            val = resolved_inputs.get(field)
            if field not in resolved_inputs or val is None or str(val).strip() in ["", "None"]:
                missing_fields.append(field)
        return missing_fields

    async def _handle_process_suspension(self, process_id: str, state: dict) -> dict:
        """Suspends process execution and dispatches an alert via the HumanManager to wait for input."""
        target_field = state["missing_inputs"][0]
        request = await self.human_manager.ask(
            process_id=process_id,
            question=f"The '{state['sub_tool']}' action requires '{target_field}'. Please provide it:"
        )

        state["request_id"] = request.request_id
        state["status"] = "waiting"
        self.state_store.save(process_id, state)

        return {
            "status": "waiting",
            "request_id": request.request_id
        }

    async def _execute_sub_tool(self, capability, state: dict, context):
        """Filters input payloads down strictly to tool parameters and triggers capability execution."""
        internal_tools = getattr(capability, "internal_tools", {})
        chosen_tool_config = internal_tools.get(state["sub_tool"], {})
        expected_fields = chosen_tool_config.get("required_fields", [])

        # Strict data filtering boundary setup
        filtered_inputs = (
            {f: state["resolved_inputs"][f] for f in expected_fields if f in state["resolved_inputs"]}
            if expected_fields else state["resolved_inputs"]
        )

        # Invoke based on the capability style mapping format
        if internal_tools:
            return await capability.execute(context=context, sub_tool=state["sub_tool"], inputs=filtered_inputs)
        return await capability.execute(context=context, inputs=filtered_inputs)