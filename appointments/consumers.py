"""
WebSocket Consumer for Real-Time Chat during Video Consultations
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for video call chat.
    Each appointment has its own chat room.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get appointment ID from URL
        self.appointment_id = self.scope['url_route']['kwargs']['appointment_id']
        self.room_group_name = f'chat_{self.appointment_id}'
        
        # Verify user has access to this appointment
        has_access = await self.check_appointment_access()
        
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send chat history when user connects
        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message = data['message']
        sender_type = data['sender_type']
        sender_name = data['sender_name']
        
        # Save message to database
        await self.save_message(message, sender_type, sender_name)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_type': sender_type,
                'sender_name': sender_name,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    async def chat_message(self, event):
        """Receive message from room group and send to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sender_type': event['sender_type'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def check_appointment_access(self):
        """Verify user has access to this appointment (is doctor or patient)"""
        from .models import Appointment
        
        user = self.scope['user']
        
        if not user.is_authenticated:
            return False
        
        try:
            appointment = Appointment.objects.get(id=self.appointment_id)
            
            # Check if user is the patient or doctor
            is_patient = appointment.user == user
            is_doctor = appointment.doctor.user == user
            
            return is_patient or is_doctor
        except Appointment.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, message, sender_type, sender_name):
        """Save chat message to database"""
        from .models import ChatMessage, Appointment
        
        appointment = Appointment.objects.get(id=self.appointment_id)
        
        ChatMessage.objects.create(
            appointment=appointment,
            sender_type=sender_type,
            sender_name=sender_name,
            message=message
        )
    
    @database_sync_to_async
    def get_chat_history(self):
        """Retrieve chat history for this appointment"""
        from .models import ChatMessage
        
        messages = ChatMessage.objects.filter(
            appointment_id=self.appointment_id
        ).order_by('timestamp')[:100]  # Last 100 messages
        
        return [
            {
                'message': msg.message,
                'sender_type': msg.sender_type,
                'sender_name': msg.sender_name,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
