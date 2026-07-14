import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()
highlighter_port = int(os.getenv("HIGHLIGHTER_PORT"))

app = FastAPI(root_path="/highlighter")

# Global state to hold the active UI updates
connected_clients = set()

class HighlightRange(BaseModel):
    start: int
    length: int

class HighlightRequest(BaseModel):
    text: str
    ranges: List[HighlightRange]

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("index.html", "r") as f:
        return f.read()

# REST Endpoint for your Python scripts
@app.post("/api/highlight")
async def update_highlight(payload: HighlightRequest):
    # Broadcast the payload to the open UI instances
    data = payload.model_dump()
    for queue in connected_clients:
        await queue.put(data)
    return {"status": "success", "message": "UI updated"}

# Server-Sent Events (SSE) route to push changes instantly to the browser
@app.get("/api/stream")
async def stream_events(request: Request):
    queue = asyncio.Queue()
    connected_clients.add(queue)
    
    async def event_generator():
        try:
            while True:
                # If client disconnects, break loop
                if await request.is_disconnected():
                    break
                data = await queue.get()
                yield f"data: {asyncio.json.dumps(data)}\n\n"
        finally:
            connected_clients.remove(queue)
            
    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=highlighter_port, reload=True)