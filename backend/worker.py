from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "Inventory Management",
    broker=f"redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/0",  # Redis should be running
    backend=f"redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/0"
)

import tasks

if __name__ == '__main__':
    celery.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo'  # or eventlet for async tasks
    ])