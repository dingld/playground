import uvicorn
from fastapi import FastAPI

from scraperx.controller import tasks, html_parser, scrape_endpoint
from scraperx.dao import session
from scraperx.utils.config import read_config_key, set_config_level_fmt

app = FastAPI()
app.mount("/api/v1/admin/tasks", tasks.app, "tasks")
app.mount("/api/v1/admin/html_parser", html_parser.app, "html_parser")
app.mount("/api/v1/admin/scrape_endpoint", scrape_endpoint.app, "scrape_endpoint")


@app.on_event("startup")
async def startup_event():
    set_config_level_fmt()
    session.bind_url()


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = read_config_key(key="log.fmt")
    uvicorn.run(app, port=9090, log_config=log_config)
