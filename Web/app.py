from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from aioredis import Redis
import asyncio, json, random


app = FastAPI()


app.mount('/static', StaticFiles(directory='static'), name='static')
render = Jinja2Templates(directory="templates").TemplateResponse


class SocketManager(object):
	"""docstring for SocketManager"""
	def __init__(self):
		super(SocketManager, self).__init__()
		self.Sockets = []
		
	async def Connect(self, Socket, name=""):
		Id = uuid4().hex
		name = f"{name}--{random.randint(10, 1000)}"

		self.Sockets.append({
			"id" : Id ,
			"Sockets" : Socket,
			"name" : name
		})
		return {'Id' : Id, 'name' : name}

	async def Send(self, Id, message):
		for _ in self.Sockets:
			if Id == _.get('id'):
				await _['Sockets'].send_bytes(json.dumps(message))
				break

	async def Broadcast(self, message):
		for _ in self.Sockets:
			await _['Sockets'].send_bytes(json.dumps(message))

	async def Deconnect(self, id = ""):
		for index, _ in enumerate(self.Sockets):
			if id == _.get('id'):
				self.Sockets.pop(index)

Manager = SocketManager()


@app.get('/', response_class=HTMLResponse)
async def Home(request : Request):
	return render('index.html', {"request" : request})

@app.websocket('/ws')
async def Stream(websocket : WebSocket):
	await websocket.accept()

	login_data = await websocket.receive_text()
	login_data = json.loads(login_data)
	if "username" in login_data:
		data = await Manager.Connect(websocket, login_data.get('username'))
		Id = data.get('Id')

		await Manager.Send(Id , {
			'MyId' : True ,
			'data' : data,
			'watchers' : [ { 'Id' : wtr.get('id'), 'name' : wtr.get('name') } for wtr in Manager.Sockets ]
		})
		
		await Manager.Broadcast({
			"NewUser" : True,
			"User" : data
		})

		print({
			'MyId' : True ,
			'data' : data,
			'watchers' : [ { 'Id' : wtr.get('Id'), 'name' : wtr.get('name') } for wtr in Manager.Sockets ]
		})

	while True:
		try:
			message = await websocket.receive_text()
			message = json.loads(message)
			print(message, type(message))
		except WebSocketDisconnect:
			print(f'User {Id} Disconnected !')
			await Manager.Deconnect(Id)
			break
		except Exception as error:
			print(error)
			await Manager.Deconnect(Id)
			break
	
	await Manager.Broadcast({'UserDisconnect' : True, 'Id' : Id})

async def BROADCAST_MSG():
	redis = Redis()
	subscriber = redis.pubsub()
	await subscriber.subscribe('COMPUTER_VISION')
	

	while True:
		try:
			msg = await subscriber.get_message(ignore_subscribe_messages=True)
			if msg:
				data = json.loads(msg.get('data'))
				await Manager.Broadcast(data)
		except Exception as error:
			print(error)


asyncio.get_event_loop().create_task(BROADCAST_MSG())