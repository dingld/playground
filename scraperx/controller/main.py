import uvicorn
from fastapi import FastAPI

from scraperx.controller import tasks, html_parser
from scraperx.dao import session

app = FastAPI()
app.mount("/api/v1/admin/tasks", tasks.app, "tasks")
app.mount("/api/v1/admin/html_parser", html_parser.app, "parser")


@app.on_event("startup")
async def startup_event():
    session.bind_url()


if __name__ == '__main__':
    uvicorn.run(app, port=9090)
