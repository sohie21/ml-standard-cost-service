from prefect import flow, task

from src.train import main as train_model


@task
def train_task() -> None:
    train_model()


@flow(name="standard-cost-retraining-pipeline")
def retraining_pipeline() -> None:
    train_task()


if __name__ == "__main__":
    retraining_pipeline()
