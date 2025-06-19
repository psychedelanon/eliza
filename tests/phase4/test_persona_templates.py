#!/usr/bin/env python3
"""
Unit tests for Phase 4: Persona Templates
Run with: python -m pytest tests/phase4/test_persona_templates.py -v
"""

import pytest
import yaml
from pathlib import Path

class TestPersonaTemplates:
    """Test persona template loading and validation."""
    
    def test_all_agent_personas_exist(self):
        """Test that all expected agent persona files exist."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        
        expected_agents = ["agent1", "agent2", "agent3", "agent4", "agent5"]
        
        for agent in expected_agents:
            persona_file = persona_dir / f"{agent}.yml"
            assert persona_file.exists(), f"Persona file missing for {agent}"
    
    def test_persona_template_mandatory_keys(self):
        """Test that all persona templates have mandatory keys."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        
        mandatory_keys = ["tone", "style_markers", "formats", "argument_chance"]
        
        for persona_file in persona_dir.glob("agent*.yml"):
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = yaml.safe_load(f)
            
            for key in mandatory_keys:
                assert key in persona, f"Missing mandatory key '{key}' in {persona_file.name}"
    
    def test_persona_argument_chance_valid(self):
        """Test that argument_chance is a valid probability."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        
        for persona_file in persona_dir.glob("agent*.yml"):
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = yaml.safe_load(f)
            
            argument_chance = persona.get("argument_chance", 0.0)
            assert 0.0 <= argument_chance <= 1.0, f"Invalid argument_chance in {persona_file.name}: {argument_chance}"
    
    def test_persona_formats_structure(self):
        """Test that formats have proper structure."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        
        for persona_file in persona_dir.glob("agent*.yml"):
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = yaml.safe_load(f)
            
            formats = persona.get("formats", [])
            assert isinstance(formats, list), f"formats should be a list in {persona_file.name}"
            
            for fmt in formats:
                assert "type" in fmt, f"Format missing 'type' in {persona_file.name}"
                assert fmt["type"] in ["single", "thread", "meme_image", "poll"], f"Invalid format type in {persona_file.name}: {fmt['type']}"
    
    def test_agent2_special_config(self):
        """Test that Agent2 (price bot) has special configuration."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        agent2_file = persona_dir / "agent2.yml"
        
        with open(agent2_file, 'r', encoding='utf-8') as f:
            persona = yaml.safe_load(f)
        
        # Agent2 should not argue (it's a price bot)
        assert persona["argument_chance"] == 0.0, "Agent2 should not have arguments"
        
        # Should be data-driven
        assert persona["tone"] == "data-driven", "Agent2 should be data-driven"
    
    def test_meme_lord_style_markers(self):
        """Test that MemeLord (Agent3) has proper meme style."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        agent3_file = persona_dir / "agent3.yml"
        
        with open(agent3_file, 'r', encoding='utf-8') as f:
            persona = yaml.safe_load(f)
        
        style_markers = persona.get("style_markers", [])
        
        # Check for meme-specific markers
        assert "all-lowercase" in style_markers, "MemeLord should use all-lowercase"
        assert "🚀" in style_markers, "MemeLord should use rocket emoji"
        assert persona["tone"] == "sarcastic meme-lord", "MemeLord should have sarcastic tone"
    
    def test_persona_voice_patterns_exist(self):
        """Test that personas with voice patterns have valid patterns."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        
        for persona_file in persona_dir.glob("agent*.yml"):
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = yaml.safe_load(f)
            
            voice_patterns = persona.get("voice_patterns", [])
            if voice_patterns:
                assert isinstance(voice_patterns, list), f"voice_patterns should be a list in {persona_file.name}"
                for pattern in voice_patterns:
                    assert isinstance(pattern, str), f"Voice pattern should be string in {persona_file.name}"
                    assert len(pattern) > 0, f"Empty voice pattern in {persona_file.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 