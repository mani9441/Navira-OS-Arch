import asyncio
import sys

from runtime import context_engine

from runtime.kernel import NaviraKernal
from runtime.orchestrator import Orchestrator
from runtime.process_manager import ProcessManager
from runtime.runtime_executor import RuntimeExecutor
from runtime.execution_resolver import ExecutionResolver

from scheduler.scheduler import Scheduler

from messaging.event_bus import EventBus
from messaging.event_manager import EventManager

from memory.memory_manager import MemoryManager
from resources.resource_manager import ResourceManager

from capabilities.registry.capability_registry import CapabilityRegistry
from registry.workflow_registry import WorkflowRegistry
from registry.team_registry import TeamRegistry

from capabilities.capability_runtime import CapabilityRuntime
from workflows.workflow_runtime import WorkflowRuntime
from teams.team_runtime import TeamRuntime

from capabilities.weather_capability import WeatherCapability
from workflows.irrigation_workflow import IrrigationWorkflow
from teams.research_team.research_team import ResearchTeam

from handlers.scheduler_event_handler import SchedulerEventHandler
from human.human_manager import HumanManager

# --- Added the Agent import ---
from agents.conversation_agent import ConversationAgent


async def shell(conversation_agent: ConversationAgent):
    """Handles the interactive CLI loop for the Foundra agent."""
    while True:
        # Prevents blocking the async loop waiting for terminal input
        query = await asyncio.to_thread(input, "\nFoundra > ")

        if query.strip().lower() == "exit":
            print("Exiting Foundra...")
            break

        if not query.strip():
            continue

        result = await conversation_agent.handle_message(query=query)

        if result.success:
            print(f"Process Started: {result.process_id}")
        else:
            print(f"Error: {result.error}")


async def main():
    # --------------------------------------------------
    # CORE OS SERVICES
    # --------------------------------------------------
    process_manager = ProcessManager()
    scheduler = Scheduler()
    event_bus = EventBus()
    
    event_manager = EventManager(event_bus)
    
    scheduler_handler = SchedulerEventHandler(
        scheduler=scheduler, 
        process_manager=process_manager
    )

    human_manager = HumanManager(event_manager)
    memory_manager = MemoryManager()

    capability_registry = CapabilityRegistry()
    workflow_registry = WorkflowRegistry()
    team_registry = TeamRegistry()

    resource_manager = ResourceManager(
        capability_registry=capability_registry, 
        memory_manager=memory_manager
    )

    # --------------------------------------------------
    # REGISTRATIONS
    # --------------------------------------------------
    capability_registry.register(
        name="weather",
        capability=WeatherCapability(),
        keywords=["weather", "temperature", "forecast", "climate", "rain", "condition"],
        metadata={"status": "active"}
    )
    
    workflow_registry.register("crop_irrigation", IrrigationWorkflow())
    team_registry.register("research", ResearchTeam())

    event_manager.subscribe("human.requested", scheduler_handler.on_human_requested)
    event_manager.subscribe("human.responded", scheduler_handler.on_human_responded)

    # --------------------------------------------------
    # KERNEL
    # --------------------------------------------------
    kernel = NaviraKernal(
        process_manager=process_manager,
        scheduler=scheduler,
        event_manager=event_manager
    )

    # --------------------------------------------------
    # RUNTIMES
    # --------------------------------------------------
    capability_runtime = CapabilityRuntime(
        capability_registry= capability_registry,
        resource_manager=resource_manager,
        memory_manager=memory_manager,
        human_manager=human_manager
    )

    workflow_runtime = WorkflowRuntime(
        workflow_registry=workflow_registry,
        resource_manager=resource_manager,
        memory_manager=memory_manager,
        human_manager=human_manager
    )

    team_runtime = TeamRuntime(
        team_registry=team_registry,
        resource_manager=resource_manager,
        memory_manager=memory_manager,
        human_manager=human_manager
    )

    # --------------------------------------------------
    # EXECUTOR
    # --------------------------------------------------
    runtime_executor = RuntimeExecutor(
        scheduler=scheduler,
        process_manager=process_manager,
        kernel=kernel,
        capability_runtime=capability_runtime,
        workflow_runtime=workflow_runtime,
        team_runtime=team_runtime
    )

    # --------------------------------------------------
    # CONTEXT ENGINE
    # --------------------------------------------------
    context_engine_instance = context_engine.ContextEngine(
        memory_manager=memory_manager, 
        process_manager=process_manager
    )

    # --------------------------------------------------
    # ORCHESTRATOR
    # --------------------------------------------------
    orchestrator = Orchestrator(
        context_engine=context_engine_instance,
        execution_resolver=ExecutionResolver(),
        kernel=kernel,
    )

    # --------------------------------------------------
    # CONVERSATION AGENT INITIALIZATION
    # --------------------------------------------------
    # Initialized using the exact references built above
    conversation_agent = ConversationAgent(
        orchestrator=orchestrator,
        event_manager=event_manager,
        human_manager=human_manager,
        memory_manager=memory_manager
    )

    # --------------------------------------------------
    # EXECUTE PROCESS & RUN INTERACTIVE SHELL
    # --------------------------------------------------
    # Spin up your background executor loop
    executor_task = asyncio.create_task(runtime_executor.run_forever())

    print("\n--- Foundra Kernel Started ---")
    
    try:
        # Instead of a hardcoded test request + sleep, pass execution to the interactive shell
        await shell(conversation_agent)
    finally:
        # Clean up background worker tasks upon shell termination
        executor_task.cancel()
        try:
            await executor_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram forced closed. Exiting.")
        sys.exit(0)