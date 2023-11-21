import uvicorn
from fastapi import FastAPI

from scraperx.api import rule
from scraperx.api import scrape
from scraperx.dao import session
from scraperx.utils.config import read_config_key, set_config_level_fmt

app = FastAPI()
# app.mount("/api/v1/admin/tasks", tasks.app, "tasks")
app.mount("/api/v1/admin/rule", rule.app, "rule")
app.mount("/api/v1/admin/scrape", scrape.app, "scrape")


@app.on_event("startup")
async def startup_event():
    set_config_level_fmt()
    session.bind_url(read_config_key("dao.session.sqlalchemy"))


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = read_config_key(key="log.fmt")
    uvicorn.run(app, port=9090, log_config=log_config)
