"""
Event System Module for MCP
Provides an event bus for inter-component communication
"""
from typing import Dict, List, Any, Callable, Optional
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger('mcp.events')

class Event:
    """Event class representing a system event"""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        return f"Event({self.type}, {self.id})"


class EventSubscription:
    """Represents a subscription to an event"""
    
    def __init__(self, event_type: str, callback: Callable[[Event], None], subscription_id: str = None):
        self.id = subscription_id or str(uuid.uuid4())
        self.event_type = event_type
        self.callback = callback
    
    def __str__(self) -> str:
        return f"Subscription({self.event_type}, {self.id})"


class EventBus:
    """
    Event bus for publishing and subscribing to events
    
    This class provides a central hub for components to communicate
    by publishing events and subscribing to event types.
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, List[EventSubscription]] = {}
        self.event_history: List[Event] = []
        self.max_history_size = 100
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers"""
        logger.debug(f"Publishing event: {event}")
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Get subscribers for this event type
        subscribers = self.subscriptions.get(event.type, [])
        
        # Also get subscribers for wildcard events
        wildcard_subscribers = self.subscriptions.get('*', [])
        all_subscribers = subscribers + wildcard_subscribers
        
        # Notify all subscribers
        for subscription in all_subscribers:
            try:
                subscription.callback(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
    
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> EventSubscription:
        """Subscribe to an event type"""
        subscription = EventSubscription(event_type, callback)
        
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        
        self.subscriptions[event_type].append(subscription)
        logger.debug(f"Added subscription: {subscription}")
        
        return subscription
    
    def unsubscribe(self, subscription: EventSubscription) -> bool:
        """Unsubscribe from an event type"""
        event_type = subscription.event_type
        
        if event_type in self.subscriptions:
            subscriptions = self.subscriptions[event_type]
            for i, sub in enumerate(subscriptions):
                if sub.id == subscription.id:
                    subscriptions.pop(i)
                    logger.debug(f"Removed subscription: {subscription}")
                    
                    # Clean up empty lists
                    if not subscriptions:
                        del self.subscriptions[event_type]
                    
                    return True
        
        return False
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 10) -> List[Event]:
        """Get recent events, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self.event_history if e.type == event_type]
            return filtered[-limit:]
        else:
            return self.event_history[-limit:]
