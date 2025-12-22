"""
Tests for dashboard WebSocket consumers
"""
from django.test import TestCase
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import json
from django.utils import timezone
from datetime import timedelta

from apps.dashboard.models import PageView, ErrorLog, AlertLog, PerformanceAlert


class DashboardConsumerTest(TestCase):
    """Test cases for DashboardConsumer"""

    def setUp(self):
        """Set up test data"""
        # Check if channels is available
        try:
            from channels.generic.websocket import AsyncWebsocketConsumer
            from apps.dashboard.consumers import DashboardConsumer
            self.has_channels = True
            self.Consumer = DashboardConsumer
        except ImportError:
            self.has_channels = False
            self.skipTest("Django Channels not installed")

    def test_consumer_class_exists(self):
        """Test that DashboardConsumer class exists"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        from apps.dashboard.consumers import DashboardConsumer
        self.assertIsNotNone(DashboardConsumer)

    @patch('apps.dashboard.consumers.DashboardConsumer.channel_layer')
    async def test_connect(self):
        """Test WebSocket connection"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.channel_name = 'test_channel'
        consumer.channel_layer = AsyncMock()
        consumer.send = AsyncMock()
        
        # Mock send_initial_data
        consumer.send_initial_data = AsyncMock()
        
        await consumer.connect()
        
        # Verify group_add was called
        consumer.channel_layer.group_add.assert_called_once()
        # Verify accept was called
        consumer.accept.assert_called_once()
        # Verify send_initial_data was called
        consumer.send_initial_data.assert_called_once()

    @patch('apps.dashboard.consumers.DashboardConsumer.channel_layer')
    async def test_disconnect(self):
        """Test WebSocket disconnection"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.channel_name = 'test_channel'
        consumer.channel_layer = AsyncMock()
        consumer.room_group_name = 'dashboard_updates'
        
        await consumer.disconnect(1000)
        
        # Verify group_discard was called
        consumer.channel_layer.group_discard.assert_called_once()

    async def test_receive_get_metrics(self):
        """Test receiving get_metrics message"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.send_metrics_update = AsyncMock()
        
        message = json.dumps({'type': 'get_metrics'})
        await consumer.receive(message)
        
        consumer.send_metrics_update.assert_called_once()

    async def test_receive_get_alerts(self):
        """Test receiving get_alerts message"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.send_alerts_update = AsyncMock()
        
        message = json.dumps({'type': 'get_alerts'})
        await consumer.receive(message)
        
        consumer.send_alerts_update.assert_called_once()

    async def test_receive_subscribe_to(self):
        """Test receiving subscribe_to message"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.subscribe_to_updates = AsyncMock()
        
        message = json.dumps({
            'type': 'subscribe_to',
            'subscription_type': 'metrics'
        })
        await consumer.receive(message)
        
        consumer.subscribe_to_updates.assert_called_once_with('metrics')

    async def test_receive_invalid_json(self):
        """Test receiving invalid JSON"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.send = AsyncMock()
        
        await consumer.receive('invalid json')
        
        # Verify error message was sent
        consumer.send.assert_called_once()
        call_args = consumer.send.call_args
        sent_data = json.loads(call_args[1]['text_data'])
        self.assertEqual(sent_data['type'], 'error')

    async def test_send_initial_data(self):
        """Test sending initial data"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.get_dashboard_metrics = AsyncMock(return_value={'test': 'data'})
        consumer.get_active_alerts = AsyncMock(return_value=[])
        consumer.send = AsyncMock()
        
        await consumer.send_initial_data()
        
        # Verify send was called
        consumer.send.assert_called_once()
        call_args = consumer.send.call_args
        sent_data = json.loads(call_args[1]['text_data'])
        self.assertEqual(sent_data['type'], 'initial_data')
        self.assertIn('metrics', sent_data)
        self.assertIn('alerts', sent_data)

    async def test_send_metrics_update(self):
        """Test sending metrics update"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.get_dashboard_metrics = AsyncMock(return_value={'test': 'data'})
        consumer.send = AsyncMock()
        
        await consumer.send_metrics_update()
        
        # Verify send was called
        consumer.send.assert_called_once()
        call_args = consumer.send.call_args
        sent_data = json.loads(call_args[1]['text_data'])
        self.assertEqual(sent_data['type'], 'metrics_update')
        self.assertIn('metrics', sent_data)

    async def test_send_alerts_update(self):
        """Test sending alerts update"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.get_active_alerts = AsyncMock(return_value=[])
        consumer.send = AsyncMock()
        
        await consumer.send_alerts_update()
        
        # Verify send was called
        consumer.send.assert_called_once()
        call_args = consumer.send.call_args
        sent_data = json.loads(call_args[1]['text_data'])
        self.assertEqual(sent_data['type'], 'alerts_update')
        self.assertIn('alerts', sent_data)

    async def test_dashboard_update(self):
        """Test handling dashboard update from group"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.send = AsyncMock()
        
        event = {'type': 'dashboard_update', 'data': 'test'}
        await consumer.dashboard_update(event)
        
        # Verify send was called with event data
        consumer.send.assert_called_once()
        call_args = consumer.send.call_args
        sent_data = json.loads(call_args[1]['text_data'])
        self.assertEqual(sent_data['type'], 'dashboard_update')

    def test_get_dashboard_metrics(self):
        """Test getting dashboard metrics"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        # Create test data
        now = timezone.now()
        today = now.date()
        
        # Create page views
        PageView.objects.create(
            path='/test/',
            load_time=1.5,
            timestamp=now
        )
        
        # Create error log
        ErrorLog.objects.create(
            error_type='TestError',
            message='Test error',
            timestamp=now
        )
        
        consumer = self.Consumer()
        
        # Test the sync version (database_sync_to_async wraps it)
        # In real async context, this would be called via await
        metrics = consumer.get_dashboard_metrics()
        
        self.assertIn('avg_load_time_today', metrics)
        self.assertIn('page_views_today', metrics)
        self.assertIn('errors_today', metrics)
        self.assertIn('recent_page_views', metrics)
        self.assertIn('recent_errors', metrics)
        self.assertIn('timestamp', metrics)

    def test_get_active_alerts(self):
        """Test getting active alerts"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        # Create test alert
        alert = PerformanceAlert.objects.create(
            alert_type='load_time',
            severity='high',
            threshold_value=5.0
        )
        
        alert_log = AlertLog.objects.create(
            alert=alert,
            message='Test alert',
            current_value=10.0,
            is_resolved=False
        )
        
        consumer = self.Consumer()
        alerts = consumer.get_active_alerts()
        
        self.assertIsInstance(alerts, list)
        if alerts:
            alert_data = alerts[0]
            self.assertIn('id', alert_data)
            self.assertIn('type', alert_data)
            self.assertIn('severity', alert_data)
            self.assertIn('message', alert_data)

    async def test_subscribe_to_updates(self):
        """Test subscribing to updates"""
        if not self.has_channels:
            self.skipTest("Django Channels not installed")
        
        consumer = self.Consumer()
        consumer.send = AsyncMock()
        
        await consumer.subscribe_to_updates('metrics')
        
        # Verify subscription confirmation was sent
        consumer.send.assert_called_once()
        call_args = consumer.send.call_args
        sent_data = json.loads(call_args[1]['text_data'])
        self.assertEqual(sent_data['type'], 'subscription_confirmed')
        self.assertEqual(sent_data['subscription_type'], 'metrics')

