import sys
import os
import asyncio
import json
import pty
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="KRAKEN Dashboard")

script_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(script_dir, "..", "web")
kraken_py = os.path.join(script_dir, "..", "kraken.py")
venv_python = os.path.join(script_dir, "..", "venv", "bin", "python")

os.makedirs(web_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=web_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(web_dir, "index.html"))

@app.websocket("/api/ws/run")
async def websocket_run(websocket: WebSocket):
    await websocket.accept()
    process = None
    master = None
    try:
        config_data = await websocket.receive_text()
        config = json.loads(config_data)
        
        module = config.get("module")
        if not module:
            await websocket.send_bytes(b"Error: No module specified.\r\n")
            return

        cmd = [venv_python, kraken_py, module]
        for k, v in config.get("args", {}).items():
            if v is not None and str(v).strip() != "":
                cmd.append(f"--{k}")
                cmd.append(str(v))
        
        master, slave = pty.openpty()
        env = os.environ.copy()
        env["FORCE_COLOR"] = "1"
        env["COLUMNS"] = "100"
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
            env=env
        )
        os.close(slave)
        
        def read_from_pty():
            try:
                return os.read(master, 1024)
            except OSError:
                return b""

        while True:
            # We must break loops if websocket is closed
            try:
                # Use wait_for to frequently check if websocket is alive
                data = await asyncio.get_event_loop().run_in_executor(None, read_from_pty)
            except Exception:
                break
            
            if not data:
                break
                
            try:
                await websocket.send_bytes(data)
            except:
                break # Client disconnected
            
        await process.wait()
        os.close(master)
        master = None
        
        if process.returncode == 0:
            await websocket.send_bytes(b"\r\n\x1b[1;32m[Process completed successfully]\x1b[0m\r\n")
        else:
             await websocket.send_bytes(f"\r\n\x1b[1;31m[Process exited with code {process.returncode}]\x1b[0m\r\n".encode())
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_bytes(f"\r\n[Error: {str(e)}]\r\n".encode())
        except:
            pass
    finally:
        if process and process.returncode is None:
            try:
                process.terminate()
            except:
                pass
        if master is not None:
            try:
                os.close(master)
            except:
                pass
