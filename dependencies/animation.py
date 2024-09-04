import websockets
import json


class Animator:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    async def connect(self):
        try:
            uri = f"ws://{self.ip}:{self.port}"
            self.ws = await websockets.connect(uri)
            await self.ws.send(json.dumps({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "auth_request",
                "messageType": "AuthenticationRequest",
                "data": {
                    "pluginName": "DaemonAnimation",
                    "pluginDeveloper": "unkou",
                    "authenticationToken": "6cff4c2a20d5aa8ad2d0165c0bc26e7fcf729ba49b0718ad3ee3aea19dc41915"
                }
            }))
            response = await self.ws.recv()
        except Exception as e:
            print(f"Error al conectar: {e}")

    async def animate(self, animation_id: int):
        await self.connect()
        try:
            await self.ws.send(json.dumps({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "start_animation_request",
                "messageType": "HotkeyTriggerRequest",
                "data": {
                    "hotkeyID": animation_id
                }
            }))
        except Exception as e:
            print(f"Error al ejecutar la animación: {e}")
