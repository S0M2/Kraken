import sys
import os
import asyncio
import json
import pty
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import asynccontextmanager

from .database import init_db, get_db, Result

script_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(script_dir, "..", "web")
kraken_py = os.path.join(script_dir, "..", "kraken.py")
venv_python = os.path.join(script_dir, "..", "venv", "bin", "python")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="KRAKEN Dashboard", lifespan=lifespan)

os.makedirs(web_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=web_dir), name="static")

@app.get("/")
async def root():
    return HTMLResponse(open(os.path.join(web_dir, "index.html")).read())

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

        modern_modules = ["ssh", "ftp", "wordpress", "wifi"]
        if module in modern_modules:
            cmd = [venv_python, kraken_py, module]
            for k, v in config.get("args", {}).items():
                if v is not None and str(v).strip() != "":
                    cmd.append(f"--{k}")
                    cmd.append(str(v))
        else:
            # Legacy routing
            wrapper_path = os.path.join(script_dir, "legacy_wrapper.py")
            target_script = os.path.join(script_dir, "..", "files", f"{module}.py")
            
            # Subdomain/Directory use _finder instead of _bruteforce, 
            # so we'll pass the exact script name from the frontend
            exact_script = config.get("script", f"{module}_bruteforce.py")
            target_script = os.path.join(script_dir, "..", "files", exact_script)
            
            cmd = [venv_python, wrapper_path, target_script, json.dumps(config.get("args", {}))]
        
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

# --- Database Endpoints ---

class ResultCreate(BaseModel):
    module: str
    target: str
    username: str
    password: str

@app.post("/api/results")
def create_result(result: ResultCreate, db: Session = Depends(get_db)):
    db_res = Result(**result.model_dump())
    db.add(db_res)
    db.commit()
    db.refresh(db_res)
    return db_res

@app.get("/api/results")
def read_results(db: Session = Depends(get_db)):
    results = db.query(Result).order_by(Result.timestamp.desc()).all()
    return results

@app.delete("/api/results/{result_id}")
def delete_result(result_id: int, db: Session = Depends(get_db)):
    res = db.query(Result).filter(Result.id == result_id).first()
    if res:
        db.delete(res)
        db.commit()
        return {"status": "deleted"}
    return {"error": "not found"}

@app.delete("/api/results")
def clear_results(db: Session = Depends(get_db)):
    db.query(Result).delete()
    db.commit()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
