from fastapi import FastAPI


from sapientone.middleware import add_used_tokens
from sapientone.routers.query import router as query_router
from sapientone.routers.memory import router as memory_router

app = FastAPI()
app.middleware("http")(add_used_tokens)
app.include_router(query_router, prefix="/query")
app.include_router(memory_router, prefix="/memory")
