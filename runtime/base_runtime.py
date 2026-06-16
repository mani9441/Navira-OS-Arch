# runtime/base_runtime.py
from runtime.process_context import ProcessContext
from runtime.runtime_result import RuntimeResult

class BaseRuntime:
    def __init__(self, registry, resource_manager, memory_manager, human_manager):
        self.registry = registry
        self.resource_manager = resource_manager
        self.memory_manager = memory_manager
        self.human_manager = human_manager

    async def execute(self, process_id, inputs=None, **kwargs):
        """
        Polymorphic executor wrapper. Handles both positional (process_id, inputs) 
        and keyword-based (context=context, inputs=inputs) execution dispatches safely.
        """
        # ─── DEFENSIVE ARGUMENT EXTRACTION ───
        # Catch cases where an upstream orchestrator passes 'context' as a keyword argument
        incoming_context = kwargs.get("context")
        
        if incoming_context and hasattr(incoming_context, "process_id"):
            # If a fully formed ProcessContext was passed directly, reuse its fields
            real_process_id = incoming_context.process_id
            real_inputs = inputs if inputs is not None else getattr(incoming_context, "inputs", {})
            context = incoming_context
        else:
            # Fallback to standard positional structural building
            real_process_id = process_id
            real_inputs = inputs or {}
            context = ProcessContext(
                process_id=real_process_id,
                inputs=real_inputs,
                resource_manager=self.resource_manager,
                memory_manager=self.memory_manager,
                human_manager=self.human_manager
            )

        try:
            # 1. Route through your 2-stage Qwen embedding resolver
            executable = await self.resolve(context)

            # 2. Forward clean instances directly to the running task worker loop
            result = await self.run(executable, context)

            return RuntimeResult(
                success=True,
                output=result
            )

        except Exception as e:
            import traceback
            print(f"[RUNTIME CRASH TRACEBACK]\n{traceback.format_exc()}")
            return RuntimeResult(
                success=False,
                error=str(e)
            )