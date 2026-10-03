from celery import Celery

celery_app = Celery(
    "ai_eval_pipeline",
    broker="amqp://guest:guest@localhost:5672//",
    backend=None,
    include=["evaluator.tasks"],
)

celery_app.conf.update(
    task_ignore_result=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)