from app import app
from fastapi_mcp import FastApiMCP

mcp = FastApiMCP(app)

mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
