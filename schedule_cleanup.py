"""Register a weekday sweep that calls a cleanup worker endpoint."""
import os

import infrai


def schedule_cleanup() -> str:
    task_url = os.environ["CLEANUP_TASK_URL"]
    job = infrai.cron.create(
        cron_expr="15 2 * * 1-5",
        task=task_url,
    )
    return job["job_id"]


if __name__ == "__main__":
    print(f"Cleanup sweep scheduled: {schedule_cleanup()}")
