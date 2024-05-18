import json

from channels.generic.websocket import AsyncWebsocketConsumer
from todo_api.models import Todo
from todo_api.serializers import TodoSerializer

class TodoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('todos', self.channel_name)
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('todos', self.channel_name)
        
    async def send_to_group(self, message):
        await self.channel_layer.group_send('todos', {
            'type': 'send_message',
            'message': 'message',
        })
    
    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'create':
            await self.create_todo(data)
        elif action == 'update':
            await self.update_todo(data)
        elif action == 'delete':
            await self.delete_todo(data)
        
    async def create_todo(self, data):
        await self.send_to_group({'action': 'create', 'todo': data})
    
    async def update_todo(self, data):
        await self.send_to_group({'action': 'update', 'todo': data})
        
    async def delete_todo(self, data):
        todo_id = data.get('id')
        await self.send_to_group({'action': 'delete', 'id': todo_id})