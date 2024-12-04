import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connection attempt received")
        print("Scope:", self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(f"Room name: {self.room_name}")
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender']
        receiver_id = text_data_json['receiver']

        # Convert IDs to email addresses
        sender_email = await self.get_user_email(sender_id)
        receiver_email = await self.get_user_email(receiver_id)

        # Save message to database
        await self.save_message(sender_email, receiver_email, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_email,
                'receiver': receiver_email
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver
        }))

    @database_sync_to_async
    def save_message(self, sender_email, receiver_email, content):
        sender = User.objects.get(email=sender_email)
        receiver = User.objects.get(email=receiver_email)
        Message.objects.create(sender=sender, receiver=receiver, content=content)

    @database_sync_to_async
    def get_user_email(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user.email
        except User.DoesNotExist:
            return None