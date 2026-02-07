import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.analysis_session.models import AnalysisSession


class SessionProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocker consumer for real-time session progress updates.

    URL: ws://localhost:8000/ws/sessions/{session_id}/
    """

    async def connect(self):
        """
        Called when WebSocket connects.
        """
        print(f"🔌 WebSocket connection attempt...")
        try:
            self.session_id = self.scope['url_route']['kwargs']['session_id']
            self.room_group_name = f"session_{self.session_id}"
            print(f"   Session ID: {self.session_id}")

            # Accept the connection first
            await self.accept()
            print(f"   ✅ Connection accepted")

            # Verify session exists
            session_exists = await self.check_session_exists()
            print(f"   Session exists: {session_exists}")
            
            if not session_exists:
                print(f"   ❌ Session not found, closing connection")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Session not found'
                }))
                await self.close()
                return
            
            # Join room group
            # A 'group' is Channels' way of broadcasting to multiple connections.
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            print(f"   ✅ Joined group: {self.room_group_name}")

            # Send initial session status
            initial_data = await self.get_session_status_data()
            if initial_data:
                await self.send(text_data=json.dumps({
                    'type': 'session_status',
                    'data': initial_data
                }))
                print(f"   ✅ Sent initial status")
            else:
                print(f"   ⚠️  No initial data to send")
                
        except Exception as e:
            print(f"   ❌ WebSocket connection error: {e}")
            import traceback
            traceback.print_exc()
            await self.close()
    
    async def disconnect(self, close_code):
        """
        Called when websocket disconnects.
        """
        # Leave the group.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # receive message from Websocket (client -> server)
    async def receive(self, text_data):
        """
        Called when client sends a message.
        """
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))
    
    # Receive message from room group (server -> client)
    async def session_update(self, event):
        """
        Handles session status updates.
        """
        await self.send(text_data=json.dumps({
            'type': 'session_update',
            'data': event['data']
        }))
    
    async def new_log(self, event):
        """
        Handles new log entries.
        """
        await self.send(text_data=json.dumps({
            'type': 'new_log',
            'data': event['data']
        }))
    
    async def analysis_complete(self, event):
        """
        Handles analysis complete signal.
        """
        await self.send(text_data=json.dumps({
            'type': 'analysis_complete',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_session_status_data(self):
        """
        Retrieve current session status from the database.
        """
        try:
            session = AnalysisSession.objects.get(session_id=self.session_id)
            return {
                'session_id': str(session.session_id),
                'status': session.status,
                'files_analyzed': session.files_analyzed,
                'total_files': session.total_files,
                'vulnerabilities_found': session.vulnerabilities_found,
            }
        except AnalysisSession.DoesNotExist:
            return None

    @database_sync_to_async
    def check_session_exists(self):
        """
        Check if the session exists in the database.
        """
        return AnalysisSession.objects.filter(
            session_id=self.session_id
        ).exists()
