import asyncio
import os
import json
from typing import List
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()
highlighter_port = int(os.getenv("HIGHLIGHTER_PORT", 8000))

app = FastAPI(root_path="/highlighter")

# Global state to hold the active UI update queues
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

# REST Endpoint for your external Python scripts to push data
@app.post("/api/highlight")
async def update_highlight(payload: HighlightRequest):
    data = payload.model_dump()
    print(f"Broadcasting to {len(connected_clients)} active UI tabs.") 
    # Broadcast the payload to all open UI instances
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
                # Optimized logic: Listens for disconnection or new items simultaneously
                get_task = asyncio.create_task(queue.get())
                disconnect_task = asyncio.create_task(request.is_disconnected())
                
                done, pending = await asyncio.wait(
                    {get_task, disconnect_task},
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Clean up unfinished tasks to prevent leaks
                for task in pending:
                    task.cancel()
                
                if disconnect_task in done and disconnect_task.result():
                    break
                    
                if get_task in done:
                    data = get_task.result()
                    # FIXED: Swapped asyncio.json with native json module
                    yield f"data: {json.dumps(data)}\n\n"
                    
        finally:
            connected_clients.remove(queue)

    # Nginx-friendly configuration headers
    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive"
    }

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream", 
        # headers=headers
    )

if __name__ == "__main__":
    # Ensure app matching your filename (e.g., if this file is named main.py, use "main:app")
    uvicorn.run("app:app", host="0.0.0.0", port=highlighter_port, reload=True)
