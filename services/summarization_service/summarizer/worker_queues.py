import queue
import threading
import time
import enum


class WorkerQueue:
    Status = enum.Enum("Status", "running stopped")

    def __init__(self, num_workers=3, idle_timeout=900, task_callback=None):
        self.tasks = queue.Queue()
        self.workers = []
        self.task_callback = task_callback
        self.num_workers = num_workers
        self.idle_timeout = idle_timeout
        self.last_task_time = time.monotonic()
        self._stop_event = threading.Event()

        self.status = self.Status.stopped

    def start(self):
        if self.status == self.Status.running:
            return
        self.status = self.Status.running
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.start()
            self.workers.append(worker)

    def stop(self):
        if self.status == self.Status.stopped:
            return
        self.status = self.Status.stopped
        self._stop_event.set()

    def join(self):
        for worker in self.workers:
            worker.join()

    def add_task(self, task):
        self.tasks.put(task)
        self.last_task_time = time.monotonic()

    def _worker_loop(self):
        while not self._stop_event.is_set():
            try:
                task = self.tasks.get(timeout=0.1)
            except queue.Empty:
                if (time.monotonic() - self.last_task_time) > self.idle_timeout:
                    self.stop()
                continue

            result = self.task_callback(task)
            # process the result as needed
            self.last_task_time = time.monotonic()
