from fastapi import WebSocket, WebSocketDisconnect
from pathlib import Path
from llama_index.core import  VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine.types import ChatMessage
from typing import Dict
from ratelimiting.ratelimiting import rate_limit

data_directory = Path("uploads")
index_directory = Path("index")
data_directory.mkdir(exist_ok=True)
index_directory.mkdir(exist_ok=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}
        self.session_memory: Dict[WebSocket, ChatMemoryBuffer] = {}
        self.indices: Dict[str, VectorStoreIndex] = {}

    async def connect(self, websocket: WebSocket, filename: str):
        await websocket.accept()
        index_path = index_directory / filename
        if not index_path.exists():
            await websocket.close(code=1008)
            return False
        self.active_connections[websocket] = filename
        # Load index and initialize chat memory for the session
        
        if index_path.exists():
            storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
            index = load_index_from_storage(storage_context)
            self.indices[filename] = index
            self.session_memory[websocket] = ChatMemoryBuffer.from_defaults(token_limit=1500)
        else:
            await websocket.close(code=1008)
            return False
        return True

    async def disconnect(self, websocket: WebSocket):
        filename = self.active_connections.pop(websocket, None)
        self.session_memory.pop(websocket, None)
        if filename:
            self.indices.pop(filename, None)
        await websocket.close()
    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)


manager = ConnectionManager()
async def handlewebsocket(websocket,filename):
    isconnected=await manager.connect(websocket, filename)
    if not isconnected:
        return
    client_ip = websocket.client.host
    try:
        while True:
            limit=await rate_limit(client_ip)
            if not limit:
               print("disconected")
               await manager.send_message(websocket, "Maximum message limit exceeds.")
               await manager.disconnect(websocket)
               return
            
            question = await websocket.receive_text()
            index = manager.indices.get(filename)
            memory = manager.session_memory.get(websocket)

            if index and memory:
                # Create chat engine with memory
                chat_engine=index.as_chat_engine(chat_mode="context",memory=memory)
                response=chat_engine.chat(question)
                memory.put(ChatMessage(content=question))
                memory.put(ChatMessage(content=response.response))
                
                await manager.send_message(websocket, f"Answer: {response.response}")
            else:
                await manager.send_message(websocket, "Session context not available.")
                await websocket.close()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

