"""
app.py — FastAPI web server for Guns, Grit & Gravity.

Each WebSocket connection is an independent game session with its own
Engine instance. The engine runs synchronously; async just handles I/O.
"""

from __future__ import annotations
import json
import sys
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.insert(0, os.path.dirname(__file__))

from engine import Engine
from web_narrator import WebNarrator

app = FastAPI(title="Guns, Grit & Gravity")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


@app.get("/")
async def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.websocket("/ws")
async def game_session(websocket: WebSocket) -> None:
    await websocket.accept()

    narrator = WebNarrator()
    engine = Engine(narrator=narrator)
    engine.start()

    # Send the title screen + initial room description
    msgs = narrator.flush()
    await websocket.send_json(msgs)

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            command = payload.get("text", "").strip()

            if not command:
                continue

            # Intercept quit before it reaches engine._quit() which calls input()
            parsed = engine.parser.parse(command)
            if parsed.verb == "quit":
                narrator.quit_message(engine.strings["quit_message"])
                msgs = narrator.flush()
                msgs.append({"type": "game_over"})
                await websocket.send_json(msgs)
                break

            engine.process(command)
            msgs = narrator.flush()

            if not engine.is_running():
                msgs.append({"type": "game_over"})
                await websocket.send_json(msgs)
                break

            await websocket.send_json(msgs)

    except WebSocketDisconnect:
        pass
