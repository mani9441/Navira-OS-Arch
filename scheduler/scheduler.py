from collections import deque
from runtime.process import ProcessStatus


class Scheduler:

    def __init__(self):
        # Queues/Stores for tracking explicit process states
        self.ready_queue = deque()
        self.running_queue = {}
        self.waiting_queue = {}
        self.paused_queue = {}

    def enqueue(self, process):
        """Pushes the process onto the ready queue."""
        self.ready_queue.append(process)

    def dequeue(self):
        if not self.ready_queue:
            return None
        return self.ready_queue.popleft()

    def mark_running(self, process_id, process):
        """Explicitly tracks that a process has moved to the active execution state."""
        self.running_queue[process_id] = process

    def mark_completed(self, process_id):
        """Cleans up the process from the running queue once execution finishes."""
        self.running_queue.pop(process_id, None)

    def dispatch(self):
        """Dequeues the next process and registers it to the running queue."""
        process = self.dequeue()
        if process is None:
            return None

        self.mark_running(process.id, process)
        return process

    def wait(self, process_id):
        """Transitions a process from RUNNING to WAITING when it blocks."""
        item = self.running_queue.pop(process_id, None)
        if item:
            self.waiting_queue[process_id] = item

    def wake(self, process_id):
        """Transitions a process from WAITING back to READY."""
        # ─── FIXED ───
        # Changed self.running_queue.pop to self.waiting_queue.pop
        item = self.waiting_queue.pop(process_id, None)
        if item:
            self.ready_queue.append(item)

    def pause(self, process_id):
        """Pauses a process from either RUNNING or READY states."""
        # Scenario A: The process is currently RUNNING
        item = self.running_queue.pop(process_id, None)

        # Scenario B: The process is still sitting in the READY queue
        if not item:
            remaining = deque()
            while self.ready_queue:
                q_item = self.ready_queue.popleft()
                if q_item.id == process_id:
                    item = q_item
                else:
                    remaining.append(q_item)
            self.ready_queue = remaining

        if item:
            self.paused_queue[process_id] = item

    def resume(self, process_id):
        """Resumes a paused process back into the READY queue."""
        item = self.paused_queue.pop(process_id, None)
        if item:
            self.ready_queue.append(item)

    # --- Metrics & Status Helpers ---

    def ready_count(self):
        return len(self.ready_queue)

    def running_count(self):
        return len(self.running_queue)

    def waiting_count(self):
        return len(self.waiting_queue)

    def paused_count(self):
        return len(self.paused_queue)

    def is_empty(self):
        return (
            self.ready_count() == 0
            and self.running_count() == 0
            and self.waiting_count() == 0
        )

    def status(self):
        return {
            "ready": self.ready_count(),
            "running": self.running_count(),
            "waiting": self.waiting_count(),
            "paused": self.paused_count(),
        }