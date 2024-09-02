import websockets
import json


class VTubeStudio:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.websocket = None
        self.payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth_request",
            "messageType": "AuthenticationTokenRequest",
        }
    
    async def connect(self):
        try:
            uri = f"ws://{self.ip}:{self.port}"
            self.websocket = await websockets.connect(uri)
        except Exception as e:
            print(f"Error al conectar: {e}")
    
    async def disconnect(self):
        await self.websocket.close()

    async def auth(self, name, developer):
        self.payload['data'] = {
            'pluginName': name,
            'pluginDeveloper': developer
        }
        await self.websocket.send(json.dumps(self.payload))
        response = await self.websocket.recv()
        self.payload['data']['authenticationToken'] = json.loads(response)['data']['authenticationToken']
        print(f"Getting token: {response}")
        
        self.payload['messageType'] = "AuthenticationRequest"
        await self.websocket.send(json.dumps(self.payload))
        response = await self.websocket.recv()
        print(f"Success login: {response}")

    async def start_animation(self, hotkey_id: str):
        self.payload['requestID'] = "start_animation_request"
        self.payload['messageType'] = "HotkeyTriggerRequest"
        self.payload['data'] = {'hotkeyID':  hotkey_id}
        await self.websocket.send(json.dumps(self.payload))


class Animator:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def animate(self, animation_id: int):
        pass

    def speak(self, animation_id: int):
        pass