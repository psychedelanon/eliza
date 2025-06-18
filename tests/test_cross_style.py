"""
Tests for cross-engagement style distribution and persona behavior.
"""

import pytest
import random
from agents.generator import get_engagement_weights, PERSONA_CONFIGS, SWARM_HANDLES


class TestEngagementWeights:
    """Test engagement weight distribution for different personas."""
    
    def test_loremaster_engagement_weights(self):
        """Test LoreMaster engagement weights."""
        weights = get_engagement_weights("LoreMaster")
        assert "quote" in weights
        assert "reply" in weights
        assert "like" in weights
        assert weights["quote"] == 0.2
        assert weights["reply"] == 0.5
        assert weights["like"] == 0.3
        assert sum(weights.values()) == 1.0
    
    def test_memelord_engagement_weights(self):
        """Test MemeLord engagement weights."""
        weights = get_engagement_weights("MemeLord")
        assert "reply" in weights
        assert "like" in weights
        assert weights["reply"] == 0.6
        assert weights["like"] == 0.4
        assert sum(weights.values()) == 1.0
    
    def test_alphascy_engagement_weights(self):
        """Test AlphaScry engagement weights."""
        weights = get_engagement_weights("AlphaScry")
        assert "reply" in weights
        assert "quote" in weights
        assert weights["reply"] == 0.7
        assert weights["quote"] == 0.3
        assert sum(weights.values()) == 1.0
    
    def test_gremlingm_engagement_weights(self):
        """Test GremlinGM engagement weights."""
        weights = get_engagement_weights("GremlinGM")
        assert "reply" in weights
        assert "like" in weights
        assert weights["reply"] == 0.8
        assert weights["like"] == 0.2
        assert sum(weights.values()) == 1.0
    
    def test_unknown_persona_weights(self):
        """Test default weights for unknown persona."""
        weights = get_engagement_weights("UnknownPersona")
        assert "like" in weights
        assert "reply" in weights
        assert "quote" in weights
        assert sum(weights.values()) == 1.0


class TestPersonaConfigs:
    """Test persona configuration data."""
    
    def test_loremaster_config(self):
        """Test LoreMaster configuration."""
        config = PERSONA_CONFIGS["LoreMaster"]
        assert config.name == "LoreMaster"
        assert "mythic lore master" in config.system_prompt.lower()
        assert "#HarryPotterObamaSonic10Inu" in config.hashtags
        assert "#BITCOIN" in config.hashtags
        assert "🔮" in config.emoji_bank
        assert config.engagement_style == "quote_tweet_20_reply_50_like_30"
    
    def test_memelord_config(self):
        """Test MemeLord configuration."""
        config = PERSONA_CONFIGS["MemeLord"]
        assert config.name == "MemeLord"
        assert "meme lord" in config.system_prompt.lower()
        assert "#HarryPotterObamaSonic10Inu" in config.hashtags
        assert "#HPOS10I" in config.hashtags
        assert "🚀" in config.emoji_bank
        assert config.engagement_style == "meme_reply_60_like_40"
    
    def test_alphascy_config(self):
        """Test AlphaScry configuration."""
        config = PERSONA_CONFIGS["AlphaScry"]
        assert config.name == "AlphaScry"
        assert "alpha scryer" in config.system_prompt.lower()
        assert "#HarryPotterObamaSonic10Inu" in config.hashtags
        assert "#Alpha" in config.hashtags
        assert "🔍" in config.emoji_bank
        assert config.engagement_style == "thread_reply_70_quote_30"
    
    def test_gremlingm_config(self):
        """Test GremlinGM configuration."""
        config = PERSONA_CONFIGS["GremlinGM"]
        assert config.name == "GremlinGM"
        assert "chaotic game master" in config.system_prompt.lower()
        assert "#HarryPotterObamaSonic10Inu" in config.hashtags
        assert "#GremlinGM" in config.hashtags
        assert "🎮" in config.emoji_bank
        assert config.engagement_style == "chaos_reply_80_like_20"
    
    def test_all_personas_have_required_hashtag(self):
        """Test that all personas include the required hashtag."""
        for persona_name, config in PERSONA_CONFIGS.items():
            assert "#HarryPotterObamaSonic10Inu" in config.hashtags, f"{persona_name} missing required hashtag"
    
    def test_all_personas_have_emojis(self):
        """Test that all personas have emoji banks."""
        for persona_name, config in PERSONA_CONFIGS.items():
            assert len(config.emoji_bank) > 0, f"{persona_name} has no emojis"
            assert all(len(emoji) > 0 for emoji in config.emoji_bank), f"{persona_name} has empty emoji"


class TestSwarmHandles:
    """Test swarm handle configuration."""
    
    def test_swarm_handles_format(self):
        """Test that all swarm handles are properly formatted."""
        for handle in SWARM_HANDLES:
            assert handle.startswith("@"), f"Handle {handle} should start with @"
            assert len(handle) > 1, f"Handle {handle} should have content after @"
    
    def test_swarm_handles_match_personas(self):
        """Test that swarm handles match persona names."""
        persona_names = set(PERSONA_CONFIGS.keys())
        handle_names = {handle[1:] for handle in SWARM_HANDLES}  # Remove @
        assert persona_names == handle_names, "Swarm handles should match persona names"


class TestEngagementDistribution:
    """Test engagement action distribution with deterministic random."""
    
    def test_loremaster_engagement_distribution(self):
        """Test LoreMaster engagement distribution over many trials."""
        random.seed(42)  # Set seed for deterministic testing
        
        actions = []
        for _ in range(1000):
            weights = get_engagement_weights("LoreMaster")
            action = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
            actions.append(action)
        
        # Count actions
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Check approximate distribution (within 5% tolerance)
        total = len(actions)
        assert abs(action_counts["quote"] / total - 0.2) < 0.05
        assert abs(action_counts["reply"] / total - 0.5) < 0.05
        assert abs(action_counts["like"] / total - 0.3) < 0.05
    
    def test_memelord_engagement_distribution(self):
        """Test MemeLord engagement distribution over many trials."""
        random.seed(42)  # Set seed for deterministic testing
        
        actions = []
        for _ in range(1000):
            weights = get_engagement_weights("MemeLord")
            action = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
            actions.append(action)
        
        # Count actions
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Check approximate distribution (within 5% tolerance)
        total = len(actions)
        assert abs(action_counts["reply"] / total - 0.6) < 0.05
        assert abs(action_counts["like"] / total - 0.4) < 0.05
    
    def test_alphascy_engagement_distribution(self):
        """Test AlphaScry engagement distribution over many trials."""
        random.seed(42)  # Set seed for deterministic testing
        
        actions = []
        for _ in range(1000):
            weights = get_engagement_weights("AlphaScry")
            action = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
            actions.append(action)
        
        # Count actions
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Check approximate distribution (within 5% tolerance)
        total = len(actions)
        assert abs(action_counts["reply"] / total - 0.7) < 0.05
        assert abs(action_counts["quote"] / total - 0.3) < 0.05
    
    def test_gremlingm_engagement_distribution(self):
        """Test GremlinGM engagement distribution over many trials."""
        random.seed(42)  # Set seed for deterministic testing
        
        actions = []
        for _ in range(1000):
            weights = get_engagement_weights("GremlinGM")
            action = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
            actions.append(action)
        
        # Count actions
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Check approximate distribution (within 5% tolerance)
        total = len(actions)
        assert abs(action_counts["reply"] / total - 0.8) < 0.05
        assert abs(action_counts["like"] / total - 0.2) < 0.05


class TestPersonaStyleConsistency:
    """Test consistency of persona styles and configurations."""
    
    def test_persona_style_uniqueness(self):
        """Test that each persona has a unique engagement style."""
        styles = [config.engagement_style for config in PERSONA_CONFIGS.values()]
        assert len(styles) == len(set(styles)), "Each persona should have a unique engagement style"
    
    def test_hashtag_diversity(self):
        """Test that personas have diverse hashtag pools."""
        all_hashtags = []
        for config in PERSONA_CONFIGS.values():
            all_hashtags.extend(config.hashtags)
        
        # Should have some unique hashtags beyond the required one
        unique_hashtags = set(all_hashtags)
        assert len(unique_hashtags) > 4, "Should have diverse hashtag selection"
    
    def test_emoji_diversity(self):
        """Test that personas have diverse emoji banks."""
        all_emojis = []
        for config in PERSONA_CONFIGS.values():
            all_emojis.extend(config.emoji_bank)
        
        # Should have diverse emoji selection
        unique_emojis = set(all_emojis)
        assert len(unique_emojis) > 10, "Should have diverse emoji selection"
    
    def test_system_prompt_uniqueness(self):
        """Test that each persona has a unique system prompt."""
        prompts = [config.system_prompt for config in PERSONA_CONFIGS.values()]
        assert len(prompts) == len(set(prompts)), "Each persona should have a unique system prompt" 