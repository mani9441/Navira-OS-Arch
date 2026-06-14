from runtime.execution_request import ExecutionRequest
from runtime.execution_result import ExecutionResult
from runtime.process_context import ProcessContext

class Orchestrator:

    def __init__(
        self,
        context_engine,
        execution_resolver,
        kernel
    ):
        self.context_engine = context_engine
        self.execution_resolver = execution_resolver
        self.kernel = kernel

    def _build_request(
            self,
            strategy,
            query
        ):

        return ExecutionRequest(

            process_type=
                strategy["process_type"],

            inputs={
                "query": query
            }
        )

    async def handle_request(
        self,
        query,
        user_id,
        conversation_id
    ):
        # 1. Gather raw inputs for context initialization
        raw_inputs = {
            "query": query,
            "user_id": user_id,
            "conversation_id": conversation_id
        }

        # 2. Build process context using incoming parameters
        process_context = ProcessContext(
            inputs=raw_inputs
        )

        # 3. Resolve the architectural strategy based on that context
        strategy = self.execution_resolver.resolve(
            context=process_context
        )

        # 4. Now we can safely build the Execution Request with the strategy target
        execution_request = self._build_request(
            strategy,
            query
        )

        try:
            # 5. Hand it over to the kernel engine instance
            process = await self.kernel.create_process(
                process_type=execution_request.process_type,
                context=process_context,
                metadata={}
            )
            
            return ExecutionResult(
                success=True,
                process_id=process.id
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )