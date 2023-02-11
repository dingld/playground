from fastapi import FastAPI
import uvicorn

from scraperx.dao import session
from scraperx.controller import tasks

app = FastAPI()
app.mount("/api/v1/admin/tasks", tasks.app, "tasks")


@app.on_event("startup")
async def startup_event():
    session.bind_url()


if __name__ == '__main__':
    uvicorn.run(app, port=9090)
