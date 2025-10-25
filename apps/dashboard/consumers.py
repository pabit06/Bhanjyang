# WebSocket consumer for real-time dashboard updates
# Note: This requires Django Channels to be installed
# For now, this is a placeholder that can be enabled when channels is available

try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    from channels.db import database_sync_to_async
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Avg, Count
    from apps.dashboard.models import PageView, ErrorLog, AlertLog
    
    class DashboardConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            self.room_group_name = 'dashboard_updates'
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send initial data
            await self.send_initial_data()

        async def disconnect(self, close_code):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        async def receive(self, text_data):
            try:
                import json
                text_data_json = json.loads(text_data)
                message_type = text_data_json.get('type')
                
                if message_type == 'get_metrics':
                    await self.send_metrics_update()
                elif message_type == 'get_alerts':
                    await self.send_alerts_update()
                elif message_type == 'subscribe_to':
                    subscription_type = text_data_json.get('subscription_type')
                    await self.subscribe_to_updates(subscription_type)
                    
            except json.JSONDecodeError:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON'
                }))

        async def send_initial_data(self):
            """Send initial dashboard data"""
            metrics = await self.get_dashboard_metrics()
            alerts = await self.get_active_alerts()
            
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'metrics': metrics,
                'alerts': alerts
            }))

        async def send_metrics_update(self):
            """Send updated metrics"""
            metrics = await self.get_dashboard_metrics()
            
            await self.send(text_data=json.dumps({
                'type': 'metrics_update',
                'metrics': metrics
            }))

        async def send_alerts_update(self):
            """Send updated alerts"""
            alerts = await self.get_active_alerts()
            
            await self.send(text_data=json.dumps({
                'type': 'alerts_update',
                'alerts': alerts
            }))

        async def dashboard_update(self, event):
            """Handle dashboard update from group"""
            await self.send(text_data=json.dumps(event))

        @database_sync_to_async
        def get_dashboard_metrics(self):
            """Get current dashboard metrics"""
            now = timezone.now()
            today = now.date()
            week_ago = now - timedelta(days=7)
            
            # Page load performance
            avg_load_time_today = PageView.objects.filter(
                timestamp__date=today
            ).aggregate(avg=Avg('load_time'))['avg'] or 0
            
            # Page views
            page_views_today = PageView.objects.filter(
                timestamp__date=today
            ).count()
            
            # Error tracking
            errors_today = ErrorLog.objects.filter(
                timestamp__date=today
            ).count()
            
            # Recent activity (last 5 minutes)
            five_minutes_ago = now - timedelta(minutes=5)
            recent_page_views = PageView.objects.filter(
                timestamp__gte=five_minutes_ago
            ).count()
            
            recent_errors = ErrorLog.objects.filter(
                timestamp__gte=five_minutes_ago
            ).count()
            
            return {
                'avg_load_time_today': round(avg_load_time_today, 2),
                'page_views_today': page_views_today,
                'errors_today': errors_today,
                'recent_page_views': recent_page_views,
                'recent_errors': recent_errors,
                'timestamp': now.isoformat()
            }

        @database_sync_to_async
        def get_active_alerts(self):
            """Get active alerts"""
            alerts = AlertLog.objects.filter(
                is_resolved=False
            ).order_by('-triggered_at')[:10]
            
            alert_data = []
            for alert in alerts:
                alert_data.append({
                    'id': alert.id,
                    'type': alert.alert.alert_type,
                    'severity': alert.alert.severity,
                    'message': alert.message,
                    'current_value': alert.current_value,
                    'threshold': alert.alert.threshold_value,
                    'triggered_at': alert.triggered_at.isoformat(),
                })
            
            return alert_data

        async def subscribe_to_updates(self, subscription_type):
            """Subscribe to specific update types"""
            # This could be expanded to handle different subscription types
            # For now, we'll just acknowledge the subscription
            await self.send(text_data=json.dumps({
                'type': 'subscription_confirmed',
                'subscription_type': subscription_type
            }))

except ImportError:
    # Django Channels not installed - WebSocket features disabled
    print("Django Channels not installed. WebSocket features are disabled.")
    print("To enable real-time features, install: pip install channels")
    
    class DashboardConsumer:
        """Placeholder for WebSocket consumer when channels is not available"""
        pass
