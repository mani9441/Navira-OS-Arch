import asyncio
import sys

from capabilities.registry import capability_registry, initialize_and_sync_inventory, vector_db
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


async def shell(conversation_agent: ConversationAgent, human_manager: HumanManager, event_manager: EventManager):
    """Handles the interactive CLI loop with awareness of pending human input requests via Event System."""
    
    # Internal dictionary to track requests waiting for terminal response
    pending_prompts = {}

    # Event handler callbacks to keep the shell synchronized
    async def on_human_requested(event):
        req_id = event.payload.get("request_id")
        if req_id:
            pending_prompts[req_id] = event.source

    async def on_human_responded(event):
        req_id = event.payload.get("request_id")
        pending_prompts.pop(req_id, None)

    # Dynamically subscribe our shell listeners to the event pipeline
    event_manager.subscribe("human.requested", on_human_requested)
    event_manager.subscribe("human.responded", on_human_responded)

    while True:
        query = await asyncio.to_thread(input, "\nFoundra > ")
        clean_query = query.strip()

        if clean_query.lower() == "exit":
            print("Exiting Foundra...")
            break

        if not clean_query:
            continue

        # ─── STATE CHECK: IS A PROCESS WAITING ON THE TERMINAL? ───
        if pending_prompts:
            # Grab the active request ID waiting for an answer
            request_id = list(pending_prompts.keys())[0]
            process_id = pending_prompts[request_id]
            
            print(f"[REPLYING] Sending input to process {process_id} for request {request_id}...")
            
            # ─── FIXED HERE ───
            # Called '.respond()' instead of '.provide_input()' 
            # and passed 'clean_query' directly as the response string.
            await human_manager.respond(request_id=request_id, response=clean_query)
            continue

        # ─── DEFAULT ROUTE: INSTRUCTION MODE ───
        result = await conversation_agent.handle_message(query=clean_query)

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

    
    workflow_registry = WorkflowRegistry()
    team_registry = TeamRegistry()

    resource_manager = ResourceManager(
        capability_registry=capability_registry, 
        memory_manager=memory_manager
    )

    # --------------------------------------------------
    # REGISTRATIONS
    # --------------------------------------------------

    await initialize_and_sync_inventory()

        
    workflow_registry.register("crop_irrigation", IrrigationWorkflow())
    team_registry.register("research", ResearchTeam())

    # event_manager.subscribe("human.requested", scheduler_handler.on_human_requested)
    # event_manager.subscribe("human.responded", scheduler_handler.on_human_responded)

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
    # KERNEL
    # --------------------------------------------------
    kernel = NaviraKernal(
        process_manager=process_manager,
        scheduler=scheduler,
        event_manager=event_manager,
        capability_runtime=capability_runtime,
        workflow_runtime=workflow_runtime,
        team_runtime=team_runtime
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
        # Pass the event_manager to the shell so it can track request states live
        await shell(conversation_agent, human_manager, event_manager)
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