from fastapi import FastAPI

from scraperx.entities.task import TaskListResponseEntity, TaskCreateUpdateResponseEntity, TaskDeleteResponseEntity, \
    TaskToggleResponseEntity, TaskRequestEntity, TaskStatus, TaskSingleResponseEntity
from scraperx.service import task_service

app = FastAPI()


@app.get("/")
async def list_project(page: int = 1, size: int = 10) -> TaskListResponseEntity:
    return task_service.list_by_page_size(page, size)


@app.get("/{task_id}")
async def get_task(task_id: int) -> TaskSingleResponseEntity:
    return task_service.get_by_id(task_id)


@app.post("/")
async def create_task(request: TaskRequestEntity) -> TaskCreateUpdateResponseEntity:
    return task_service.create_obj(request)


@app.put("/{task_id}")
async def update_task(task_id: int, request: TaskRequestEntity) -> TaskCreateUpdateResponseEntity:
    return task_service.update_obj(task_id, request)


@app.delete("/{task_id}")
async def delete_task(task_id: int) -> TaskDeleteResponseEntity:
    return task_service.delete_by_id(task_id)


@app.post("/{task_id}/toggle/{status}")
async def toggle_task(task_id: int, status: int) -> TaskToggleResponseEntity:
    if not TaskStatus.is_legal(status):
        return TaskToggleResponseEntity.construct(ok=1, message="illegal status")
    return task_service.toggle_start_stop(task_id, status)
