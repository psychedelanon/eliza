import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .EventSystem import EventType, EventPriority, Event, event_router, register_event_handler

log = logging.getLogger("enhanced_swarm")

@dataclass
class EngagementConfig:
    """Configuration for engagement behavior."""
    min_delay: float = 30.0  # Minimum delay before engagement
    max_delay: float = 120.0  # Maximum delay before engagement
    max_concurrent: int = 3  # Maximum concurrent engagements per agent
    priority: EventPriority = EventPriority.NORMAL
    enabled: bool = True
    
    @property
    def delay_range(self) -> tuple:
        """Return delay range as a tuple for compatibility."""
        return (self.min_delay, self.max_delay)

class EnhancedSwarmCoordinator:
    """
    Enhanced swarm coordinator that enables any agent to lead and coordinates
    event-driven engagement with advanced routing and filtering.
    """
    
    def __init__(self, idx=0, name=None, personality=None, dry_run=False, agents=None, rng=None, **kwargs):
        self.idx = idx
        self.name = name or "EnhancedSwarmCoordinator"
        self.personality = personality
        self.dry_run = dry_run
        self.agents = agents if agents is not None else []
        self._rng = rng or random  # Use provided RNG or default to random module
        
        # Engagement configurations per agent type
        self.engagement_configs = {
            "LoreMaster": EngagementConfig(min_delay=45, max_delay=90, priority=EventPriority.HIGH),
            "MemeLord": EngagementConfig(min_delay=30, max_delay=75, priority=EventPriority.NORMAL),
            "AlphaScry": EngagementConfig(min_delay=60, max_delay=120, priority=EventPriority.HIGH),
            "GremlinGM": EngagementConfig(min_delay=20, max_delay=60, priority=EventPriority.NORMAL),
            "Agent2": EngagementConfig(min_delay=0, max_delay=0, priority=EventPriority.CRITICAL),  # Price posts
        }
        
        # Initialize context store
        from eliza.context.store import get_context_store
        self.context_store = get_context_store()
        
        # Register event handlers
        self._register_handlers()
        
        # Track engagement statistics
        self.engagement_stats = {
            "total_engagements": 0,
            "successful_engagements": 0,
            "failed_engagements": 0,
            "arguments_triggered": 0,
            "last_engagement": None
        }

    def _register_handlers(self) -> None:
        """Register event handlers for different event types."""
        
        # Handle agent posts (any agent can lead)
        register_event_handler(
            agent_name=self.name,
            event_types=[EventType.AGENT_POST],
            handler_func=self._handle_agent_post,
            priority=EventPriority.HIGH,
            delay_range=(0, 5)  # Quick response to posts
        )
        
        # Handle price posts (special handling for Agent2)
        register_event_handler(
            agent_name=self.name,
            event_types=[EventType.PRICE_POST],
            handler_func=self._handle_price_post,
            priority=EventPriority.CRITICAL,
            delay_range=(0, 2)
        )
        
        # Handle market signals
        register_event_handler(
            agent_name=self.name,
            event_types=[EventType.MARKET_SIGNAL],
            handler_func=self._handle_market_signal,
            priority=EventPriority.NORMAL,
            delay_range=(5, 15)
        )
        
        # Handle new hot tokens
        register_event_handler(
            agent_name=self.name,
            event_types=[EventType.NEW_HOT_TOKEN],
            handler_func=self._handle_hot_token,
            priority=EventPriority.HIGH,
            delay_range=(10, 30)
        )
        
        # Handle quality alerts
        register_event_handler(
            agent_name=self.name,
            event_types=[EventType.QUALITY_ALERT],
            handler_func=self._handle_quality_alert,
            priority=EventPriority.CRITICAL,
            delay_range=(0, 0)
        )
        
        # Handle rate limit alerts
        register_event_handler(
            agent_name=self.name,
            event_types=[EventType.RATE_LIMIT_ALERT],
            handler_func=self._handle_rate_limit_alert,
            priority=EventPriority.CRITICAL,
            delay_range=(0, 0)
        )

    async def _handle_agent_post(self, event: Event) -> None:
        """Handle any agent post and coordinate engagement."""
        source_agent = event.source_agent
        tweet_id = event.data.get("tweet_id")
        text = event.data.get("text", "")
        
        log.info(
            f"Coordinating engagement for {source_agent}'s post (ID: {tweet_id})",
            extra={
                "agent": self.name,
                "event": "coordination_started",
                "source_agent": source_agent,
                "tweet_id": tweet_id
            }
        )
        
        # Store context
        await self._store_context(source_agent, tweet_id, text)
        
        # Determine which agents should engage
        engaging_agents = self._get_engaging_agents(source_agent, event)
        
        # Check for argument trigger
        await self._maybe_trigger_argument(source_agent, tweet_id, text)
        
        # Schedule engagements with appropriate delays
        for agent_name in engaging_agents:
            config = self.engagement_configs.get(agent_name, EngagementConfig())
            if not config.enabled:
                continue
                
            delay = self._rng.uniform(config.min_delay, config.max_delay)
            
            log.debug(
                f"Scheduling engagement for {agent_name} with delay {delay:.1f}s",
                extra={
                    "agent": self.name,
                    "target_agent": agent_name,
                    "delay": delay,
                    "config": config.delay_range
                }
            )
            
            # Create engagement event with context
            engagement_event = Event(
                type=EventType.ENGAGEMENT_REQUEST,
                priority=config.priority,
                source_agent=self.name,
                target_agents=[agent_name],
                data={
                    "original_tweet_id": tweet_id,
                    "original_agent": source_agent,
                    "original_text": text,
                    "engagement_type": "reply",
                    "delay": delay,
                    "context": await self._get_engagement_context(agent_name)
                }
            )
            
            await event_router.publish_event(engagement_event)
            
            log.info(
                f"Scheduled {agent_name} to engage with {source_agent} in {delay:.1f}s",
                extra={
                    "agent": self.name,
                    "event": "engagement_scheduled",
                    "target_agent": agent_name,
                    "source_agent": source_agent,
                    "delay": delay
                }
            )

    async def _store_context(self, agent_id: str, tweet_id: int, text: str) -> None:
        """Store context information for the tweet."""
        # Extract topic tags from text
        topic_tags = self._extract_topic_tags(text)
        
        # Store in context store
        self.context_store.push(
            agent_id=agent_id,
            tweet_id=tweet_id,
            topic_tags=topic_tags,
            text=text[:200]  # Truncate long texts
        )
        
        log.debug(
            f"Stored context for {agent_id}: {topic_tags}",
            extra={
                "agent": self.name,
                "context_agent": agent_id,
                "topics": topic_tags
            }
        )

    def _extract_topic_tags(self, text: str) -> List[str]:
        """Extract topic tags from tweet text."""
        tags = []
        
        # Crypto symbols
        import re
        crypto_pattern = r'\$([A-Z]{2,10})'
        crypto_matches = re.findall(crypto_pattern, text)
        tags.extend([f"crypto_{symbol.lower()}" for symbol in crypto_matches])
        
        # Hashtags
        hashtag_pattern = r'#(\w+)'
        hashtag_matches = re.findall(hashtag_pattern, text)
        tags.extend([f"hashtag_{tag.lower()}" for tag in hashtag_matches])
        
        # Price-related
        if any(word in text.lower() for word in ['price', 'pump', 'dump', 'moon', 'dip']):
            tags.append("price_action")
        
        # Market sentiment
        if any(word in text.lower() for word in ['bullish', 'bearish', 'fud', 'fomo']):
            tags.append("market_sentiment")
        
        # Meme culture
        if any(word in text.lower() for word in ['meme', 'wagmi', 'gm', 'lfg', 'hodl']):
            tags.append("meme_culture")
        
        return tags[:5]  # Limit to 5 tags

    async def _get_engagement_context(self, agent_name: str) -> Dict[str, Any]:
        """Get contextual information for engagement."""
        # Get recent context entries
        recent_entries = self.context_store.pull_last(5)
        last_topic = self.context_store.last_topic_by_agent(agent_name)
        
        return {
            "recent_topics": [entry.topic_tags for entry in recent_entries],
            "last_agent_topic": last_topic,
            "swarm_activity": len(recent_entries)
        }

    async def _maybe_trigger_argument(self, source_agent: str, tweet_id: int, text: str) -> None:
        """Maybe trigger a fake argument based on persona argument_chance."""
        # Load source agent persona to check argument_chance
        persona = await self._load_agent_persona(source_agent)
        
        if not persona:
            return
        
        argument_chance = persona.get("argument_chance", 0.0)
        
        if self._rng.random() < argument_chance:
            # Select opponent
            available_opponents = [
                agent for agent in ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"] 
                if agent != source_agent
            ]
            
            if not available_opponents:
                return
            
            opponent = self._rng.choice(available_opponents)
            
            # Schedule argument response
            delay = self._rng.uniform(60, 120)  # 60-120s delay for argument
            
            argument_event = Event(
                type=EventType.ENGAGEMENT_REQUEST,
                priority=EventPriority.HIGH,
                source_agent=self.name,
                target_agents=[opponent],
                data={
                    "original_tweet_id": tweet_id,
                    "original_agent": source_agent,
                    "original_text": text,
                    "engagement_type": "argument",
                    "delay": delay,
                    "argument_style": "dissenting_view"
                }
            )
            
            await event_router.publish_event(argument_event)
            
            self.engagement_stats["arguments_triggered"] += 1
            
            log.info(
                f"Argument triggered: {opponent} will counter {source_agent} in {delay:.1f}s",
                extra={
                    "agent": self.name,
                    "event": "argument_triggered",
                    "source_agent": source_agent,
                    "opponent": opponent,
                    "delay": delay
                }
            )

    async def _load_agent_persona(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Load agent persona from file."""
        import yaml
        from pathlib import Path
        
        persona_file = Path(__file__).parent.parent / "persona" / f"{agent_name.lower()}.yml"
        
        if not persona_file.exists():
            # Try alternative naming
            persona_file = Path(__file__).parent.parent / "persona" / f"agent{agent_name[-1] if agent_name[-1].isdigit() else '1'}.yml"
        
        if persona_file.exists():
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                log.warning(f"Failed to load persona for {agent_name}: {e}")
        
        return None

    async def _handle_price_post(self, event: Event) -> None:
        """Handle price posts with special coordination."""
        source_agent = event.source_agent
        tweet_id = event.data.get("tweet_id")
        btc_price = event.data.get("btc_price") or event.data.get("btc")  # Use 'btc_price' key from event data
        hpo_price = event.data.get("hpo_price") or event.data.get("hpo")  # Use 'hpo_price' key from event data
        
        log.info(
            f"Coordinating price post engagement: BTC=${btc_price}, HPO=${hpo_price}",
            extra={
                "agent": self.name,
                "event": "price_coordination",
                "source_agent": source_agent,
                "tweet_id": tweet_id,
                "btc_price": btc_price,
                "hpo_price": hpo_price
            }
        )
        
        # Store price context
        await self._store_context(source_agent, tweet_id, f"Price update: BTC=${btc_price}, HPO=${hpo_price}")
        
        # All persona agents should engage with price posts
        persona_agents = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]
        
        for agent_name in persona_agents:
            config = self.engagement_configs.get(agent_name, EngagementConfig())
            if not config.enabled:
                continue
                
            delay = self._rng.uniform(config.min_delay, config.max_delay)
            
            log.debug(
                f"Scheduling price engagement for {agent_name} with delay {delay:.1f}s",
                extra={
                    "agent": self.name,
                    "target_agent": agent_name,
                    "delay": delay,
                    "btc_price": btc_price,
                    "hpo_price": hpo_price
                }
            )
            
            # Create price-specific engagement event
            engagement_event = Event(
                type=EventType.ENGAGEMENT_REQUEST,
                priority=EventPriority.HIGH,
                source_agent=self.name,
                target_agents=[agent_name],
                data={
                    "original_tweet_id": tweet_id,
                    "original_agent": source_agent,
                    "engagement_type": "price_reply",
                    "btc_price": btc_price,
                    "hpo_price": hpo_price,
                    "delay": delay
                }
            )
            
            await event_router.publish_event(engagement_event)

    async def _handle_market_signal(self, event: Event) -> None:
        """Handle market signals and coordinate appropriate responses."""
        signal_type = event.data.get("signal_type", "unknown")
        signal_value = event.data.get("value")
        
        log.info(
            f"Processing market signal: {signal_type} = {signal_value}",
            extra={
                "agent": self.name,
                "event": "market_signal",
                "signal_type": signal_type,
                "signal_value": signal_value
            }
        )
        
        # Determine which agents should respond to this signal
        responding_agents = self._get_signal_responders(signal_type)
        
        for agent_name in responding_agents:
            config = self.engagement_configs.get(agent_name, EngagementConfig())
            if not config.enabled:
                continue
                
            delay = self._rng.uniform(config.min_delay, config.max_delay)
            
            # Create market signal response event
            response_event = Event(
                type=EventType.ENGAGEMENT_REQUEST,
                priority=config.priority,
                source_agent=self.name,
                target_agents=[agent_name],
                data={
                    "engagement_type": "market_signal_response",
                    "signal_type": signal_type,
                    "signal_value": signal_value,
                    "delay": delay
                }
            )
            
            await event_router.publish_event(response_event)

    async def _handle_hot_token(self, event: Event) -> None:
        """Handle new hot token events."""
        symbol = event.data.get("symbol", "UNKNOWN")
        pct_change = event.data.get("pct", 0)
        
        log.info(
            f"Hot token detected: {symbol} up {pct_change}%",
            extra={
                "agent": self.name,
                "event": "hot_token",
                "symbol": symbol,
                "pct_change": pct_change
            }
        )
        
        # All agents can respond to hot tokens
        all_agents = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM", "Agent2"]
        
        for agent_name in all_agents:
            config = self.engagement_configs.get(agent_name, EngagementConfig())
            if not config.enabled:
                continue
                
            delay = self._rng.uniform(config.min_delay, config.max_delay)
            
            # Create hot token response event
            response_event = Event(
                type=EventType.ENGAGEMENT_REQUEST,
                priority=config.priority,
                source_agent=self.name,
                target_agents=[agent_name],
                data={
                    "engagement_type": "hot_token_response",
                    "symbol": symbol,
                    "pct_change": pct_change,
                    "delay": delay
                }
            )
            
            await event_router.publish_event(response_event)

    async def _handle_quality_alert(self, event: Event) -> None:
        """Handle quality validation alerts."""
        alert_type = event.data.get("alert_type", "unknown")
        agent_name = event.data.get("agent", "unknown")
        details = event.data.get("details", {})
        
        log.warning(
            f"Quality alert for {agent_name}: {alert_type}",
            extra={
                "agent": self.name,
                "event": "quality_alert",
                "alert_type": alert_type,
                "affected_agent": agent_name,
                "details": details
            }
        )
        
        # Could implement quality improvement strategies here
        # For now, just log the alert

    async def _handle_rate_limit_alert(self, event: Event) -> None:
        """Handle rate limit alerts."""
        agent_name = event.data.get("agent", "unknown")
        rate_limit_type = event.data.get("rate_limit_type", "unknown")
        
        log.warning(
            f"Rate limit alert for {agent_name}: {rate_limit_type}",
            extra={
                "agent": self.name,
                "event": "rate_limit_alert",
                "affected_agent": agent_name,
                "rate_limit_type": rate_limit_type
            }
        )
        
        # Could implement rate limit mitigation strategies here
        # For now, just log the alert

    def _get_engaging_agents(self, source_agent: str, event: Event) -> List[str]:
        """Determine which agents should engage with a post."""
        # Exclude the source agent
        all_agents = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]
        available_agents = [a for a in all_agents if a != source_agent]
        
        # Randomly select 2-3 agents to engage using instance RNG
        num_engagements = self._rng.randint(2, min(3, len(available_agents)))
        return self._rng.sample(available_agents, num_engagements)

    def _get_signal_responders(self, signal_type: str) -> List[str]:
        """Determine which agents should respond to market signals."""
        # Different agents respond to different signal types
        if signal_type in ["pump", "dump", "breakout"]:
            return ["AlphaScry", "MemeLord"]  # Technical signals
        elif signal_type in ["trend", "momentum"]:
            return ["LoreMaster", "GremlinGM"]  # Trend signals
        else:
            return ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]  # All agents

    async def generate_market_signals(self) -> None:
        """Generate fake market signals for testing."""
        if self.dry_run:
            signal_types = ["pump", "dump", "breakout", "trend", "momentum"]
            signal_type = self._rng.choice(signal_types)
            signal_value = self._rng.uniform(0, 100)
            
            # 20% chance of generating a signal
            if self._rng.random() < 0.2:
                await event_router.publish_event(Event(
                    type=EventType.MARKET_SIGNAL,
                    priority=EventPriority.NORMAL,
                    source_agent=self.name,
                    data={
                        "signal_type": signal_type,
                        "value": signal_value,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ))

    async def generate_hot_tokens(self) -> None:
        """Generate fake hot token events for testing."""
        if self.dry_run:
            # 30% chance of hot token event
            if self._rng.random() < 0.3:
                trending_tokens = ["DOGE", "PEPE", "BONK", "WIF", "FLOKI", "SHIB"]
                symbol = self._rng.choice(trending_tokens)
                pct_change = self._rng.randint(50, 1000)  # 50% to 1000% pump
                
                await event_router.publish_event(Event(
                    type=EventType.NEW_HOT_TOKEN,
                    priority=EventPriority.HIGH,
                    source_agent=self.name,
                    data={
                        "symbol": symbol,
                        "pct": pct_change,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ))

    def craft_post(self):
        """Return a tuple of (text, img) for compatibility with base TwitterAgent.run()."""
        return ("EnhancedSwarmCoordinator monitoring events...", None)

    async def run(self):
        """Main run loop for the enhanced swarm coordinator."""
        log.info("EnhancedSwarmCoordinator started - monitoring for events")
        
        # Start the event router
        event_router.start()
        
        try:
            while True:
                # Generate market signals and hot tokens periodically
                await self.generate_market_signals()
                await self.generate_hot_tokens()
                
                # Log statistics periodically
                stats = event_router.get_stats()
                context_stats = self.context_store.get_stats()
                
                if stats["queue_size"] > 0 or stats["active_tasks"] > 0:
                    log.info(f"Event router stats: {stats}")
                
                if context_stats["buffer_size"] > 0:
                    log.info(f"Context store stats: {context_stats}")
                
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            log.error(f"EnhancedSwarmCoordinator error: {e}")
        finally:
            event_router.stop()

    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        router_stats = event_router.get_stats()
        context_stats = self.context_store.get_stats()
        
        return {
            "coordinator": self.engagement_stats,
            "router": router_stats,
            "context": context_stats,
            "configs": {name: {
                "enabled": config.enabled,
                "priority": config.priority.value,
                "delay_range": config.delay_range
            } for name, config in self.engagement_configs.items()}
        } 