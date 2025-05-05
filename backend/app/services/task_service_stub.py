"""
Stub implementation of TaskService to use when Cloud Tasks is not available.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskService:
    """Stub implementation of TaskService that logs instead of creating real tasks."""

    def __init__(self):
        logger.warning("Using TaskService stub implementation - Cloud Tasks not available")
        self.tasks = []

    def create_task(self, queue_name, endpoint, payload, delay_seconds=0):
        """Log the task instead of creating it in Cloud Tasks."""
        scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)
        task_id = f"stub-task-{len(self.tasks)+1}"

        logger.info(
            f"STUB TASK CREATED - ID: {task_id}, "
            f"Queue: {queue_name}, "
            f"Endpoint: {endpoint}, "
            f"Scheduled: {scheduled_time}, "
            f"Payload size: {len(str(payload))} bytes"
        )

        self.tasks.append({
            "id": task_id,
            "queue": queue_name,
            "endpoint": endpoint,
            "scheduled_time": scheduled_time,
            "payload": payload,
        })

        return task_id
