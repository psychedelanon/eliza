"""
Tests for configuration schema validation.

Ensures that Pydantic schemas correctly validate persona and engagement configurations.
"""

import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError
from eliza.config.schema import (
    PersonaSchema, 
    FormatConfig, 
    EngagementConfigSchema,
    validate_persona_file,
    validate_all_personas,
    validate_engagement_config,
    get_schema_summary
)


class TestFormatConfig:
    """Test FormatConfig schema validation."""
    
    def test_valid_format_config(self):
        """Test valid format configuration."""
        config = FormatConfig(
            type="thread",
            max_tweets=5,
            probability=0.8
        )
        assert config.type == "thread"
        assert config.max_tweets == 5
        assert config.probability == 0.8
    
    def test_minimal_format_config(self):
        """Test minimal format configuration."""
        config = FormatConfig(type="single")
        assert config.type == "single"
        assert config.max_tweets is None
        assert config.probability is None
    
    def test_invalid_format_type(self):
        """Test invalid format type."""
        with pytest.raises(ValidationError):
            FormatConfig(type="invalid_type")
    
    def test_invalid_max_tweets(self):
        """Test invalid max_tweets values."""
        with pytest.raises(ValidationError):
            FormatConfig(type="thread", max_tweets=0)  # Too low
            
        with pytest.raises(ValidationError):
            FormatConfig(type="thread", max_tweets=15)  # Too high
    
    def test_invalid_probability(self):
        """Test invalid probability values."""
        with pytest.raises(ValidationError):
            FormatConfig(type="single", probability=-0.1)  # Too low
            
        with pytest.raises(ValidationError):
            FormatConfig(type="single", probability=1.5)  # Too high


class TestPersonaSchema:
    """Test PersonaSchema validation."""
    
    def test_valid_persona_schema(self):
        """Test valid persona configuration."""
        config = {
            "tone": "sarcastic meme-lord",
            "style_markers": ["lowkey", "ngl", "fr fr"],
            "formats": [
                {"type": "single"},
                {"type": "thread", "max_tweets": 3, "probability": 0.3}
            ],
            "argument_chance": 0.15
        }
        persona = PersonaSchema(**config)
        assert persona.tone == "sarcastic meme-lord"
        assert len(persona.style_markers) == 3
        assert len(persona.formats) == 2
        assert persona.argument_chance == 0.15
    
    def test_minimal_persona_schema(self):
        """Test minimal valid persona configuration."""
        config = {
            "tone": "analytical",
            "style_markers": ["data-driven"],
            "formats": [{"type": "single"}],
            "argument_chance": 0.0
        }
        persona = PersonaSchema(**config)
        assert persona.tone == "analytical"
        assert persona.allowed_refs == []
        assert persona.voice_patterns == []
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        # Missing tone
        with pytest.raises(ValidationError):
            PersonaSchema(
                style_markers=["test"],
                formats=[{"type": "single"}],
                argument_chance=0.1
            )
        
        # Missing style_markers
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="test",
                formats=[{"type": "single"}],
                argument_chance=0.1
            )
        
        # Missing formats
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="test",
                style_markers=["test"],
                argument_chance=0.1
            )
        
        # Missing argument_chance
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="test",
                style_markers=["test"],
                formats=[{"type": "single"}]
            )
    
    def test_empty_tone_validation(self):
        """Test that empty tone strings are rejected."""
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="",
                style_markers=["test"],
                formats=[{"type": "single"}],
                argument_chance=0.1
            )
        
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="   ",  # Whitespace only
                style_markers=["test"],
                formats=[{"type": "single"}],
                argument_chance=0.1
            )
    
    def test_empty_style_markers_validation(self):
        """Test that empty style markers are rejected."""
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="test",
                style_markers=[],
                formats=[{"type": "single"}],
                argument_chance=0.1
            )
        
        with pytest.raises(ValidationError):
            PersonaSchema(
                tone="test",
                style_markers=["", "  "],  # All empty/whitespace
                formats=[{"type": "single"}],
                argument_chance=0.1
            )
    
    def test_invalid_argument_chance(self):
        """Test invalid argument_chance values."""
        config_base = {
            "tone": "test",
            "style_markers": ["test"],
            "formats": [{"type": "single"}]
        }
        
        # Too low
        with pytest.raises(ValidationError):
            PersonaSchema(**{**config_base, "argument_chance": -0.1})
        
        # Too high
        with pytest.raises(ValidationError):
            PersonaSchema(**{**config_base, "argument_chance": 1.5})
    
    def test_format_probability_validation(self):
        """Test format probability sum validation."""
        config_base = {
            "tone": "test",
            "style_markers": ["test"],
            "argument_chance": 0.1
        }
        
        # Probabilities sum to > 1.0
        with pytest.raises(ValidationError):
            PersonaSchema(**{
                **config_base,
                "formats": [
                    {"type": "single", "probability": 0.7},
                    {"type": "thread", "probability": 0.5}  # 0.7 + 0.5 = 1.2 > 1.0
                ]
            })


class TestEngagementConfigSchema:
    """Test EngagementConfigSchema validation."""
    
    def test_valid_engagement_config(self):
        """Test valid engagement configuration."""
        config = {
            "min_delay": 60.0,
            "max_delay": 180.0,
            "max_concurrent": 5,
            "priority": "HIGH",
            "enabled": True
        }
        engagement = EngagementConfigSchema(**config)
        assert engagement.min_delay == 60.0
        assert engagement.max_delay == 180.0
        assert engagement.max_concurrent == 5
        assert engagement.priority == "HIGH"
        assert engagement.enabled is True
    
    def test_minimal_engagement_config(self):
        """Test minimal engagement configuration."""
        config = {
            "min_delay": 30.0,
            "max_delay": 60.0
        }
        engagement = EngagementConfigSchema(**config)
        assert engagement.min_delay == 30.0
        assert engagement.max_delay == 60.0
        assert engagement.max_concurrent == 3  # Default
        assert engagement.priority == "NORMAL"  # Default
        assert engagement.enabled is True  # Default
    
    def test_invalid_delay_range(self):
        """Test that max_delay < min_delay is rejected."""
        with pytest.raises(ValidationError):
            EngagementConfigSchema(
                min_delay=100.0,
                max_delay=50.0  # Less than min_delay
            )
    
    def test_invalid_priority(self):
        """Test invalid priority values."""
        with pytest.raises(ValidationError):
            EngagementConfigSchema(
                min_delay=60.0,
                max_delay=120.0,
                priority="INVALID"
            )
    
    def test_invalid_max_concurrent(self):
        """Test invalid max_concurrent values."""
        with pytest.raises(ValidationError):
            EngagementConfigSchema(
                min_delay=60.0,
                max_delay=120.0,
                max_concurrent=0  # Too low
            )
        
        with pytest.raises(ValidationError):
            EngagementConfigSchema(
                min_delay=60.0,
                max_delay=120.0,
                max_concurrent=15  # Too high
            )


class TestFileValidation:
    """Test file-based validation functions."""
    
    def test_validate_persona_file_success(self, tmp_path):
        """Test successful persona file validation."""
        # Create a valid persona file
        persona_data = {
            "tone": "cryptic-sage",
            "style_markers": ["ancient wisdom", "mystical"],
            "formats": [{"type": "single"}],
            "argument_chance": 0.05
        }
        
        persona_file = tmp_path / "agent1.yml"
        with open(persona_file, 'w') as f:
            yaml.dump(persona_data, f)
        
        persona = validate_persona_file(persona_file)
        assert persona.tone == "cryptic-sage"
        assert persona.argument_chance == 0.05
    
    def test_validate_persona_file_not_found(self, tmp_path):
        """Test persona file not found error."""
        non_existent_file = tmp_path / "missing.yml"
        
        with pytest.raises(FileNotFoundError):
            validate_persona_file(non_existent_file)
    
    def test_validate_persona_file_invalid_yaml(self, tmp_path):
        """Test invalid YAML file."""
        persona_file = tmp_path / "invalid.yml"
        with open(persona_file, 'w') as f:
            f.write("tone: test\n  invalid: yaml: syntax:")
        
        with pytest.raises(yaml.YAMLError):
            validate_persona_file(persona_file)
    
    def test_validate_persona_file_empty(self, tmp_path):
        """Test empty YAML file."""
        persona_file = tmp_path / "empty.yml"
        with open(persona_file, 'w') as f:
            f.write("")
        
        with pytest.raises(ValidationError):
            validate_persona_file(persona_file)
    
    def test_validate_all_personas_success(self, tmp_path):
        """Test successful validation of all persona files."""
        # Create multiple valid persona files
        personas_data = [
            {
                "tone": "analytical",
                "style_markers": ["data-driven"],
                "formats": [{"type": "single"}],
                "argument_chance": 0.08
            },
            {
                "tone": "chaotic-playful",
                "style_markers": ["gm fren", "wagmi"],
                "formats": [{"type": "thread", "max_tweets": 3}],
                "argument_chance": 0.12
            }
        ]
        
        for i, data in enumerate(personas_data, 1):
            persona_file = tmp_path / f"agent{i}.yml"
            with open(persona_file, 'w') as f:
                yaml.dump(data, f)
        
        personas = validate_all_personas(tmp_path)
        assert len(personas) == 2
        assert "agent1" in personas
        assert "agent2" in personas
        assert personas["agent1"].tone == "analytical"
        assert personas["agent2"].tone == "chaotic-playful"
    
    def test_validate_all_personas_no_directory(self, tmp_path):
        """Test validation with non-existent directory."""
        non_existent_dir = tmp_path / "missing"
        
        with pytest.raises(FileNotFoundError):
            validate_all_personas(non_existent_dir)
    
    def test_validate_all_personas_no_files(self, tmp_path):
        """Test validation with no agent files."""
        # Create directory but no agent*.yml files
        (tmp_path / "other.yml").write_text("test")
        
        with pytest.raises(FileNotFoundError):
            validate_all_personas(tmp_path)
    
    def test_validate_all_personas_mixed_validity(self, tmp_path):
        """Test validation with mix of valid and invalid files."""
        # Valid file
        valid_data = {
            "tone": "test",
            "style_markers": ["test"],
            "formats": [{"type": "single"}],
            "argument_chance": 0.1
        }
        valid_file = tmp_path / "agent1.yml"
        with open(valid_file, 'w') as f:
            yaml.dump(valid_data, f)
        
        # Invalid file
        invalid_file = tmp_path / "agent2.yml"
        with open(invalid_file, 'w') as f:
            f.write("incomplete: data")
        
        with pytest.raises(ValidationError) as exc_info:
            validate_all_personas(tmp_path)
        
        assert "agent2.yml" in str(exc_info.value)


class TestEngagementValidation:
    """Test engagement configuration validation."""
    
    def test_validate_engagement_config_success(self):
        """Test successful engagement config validation."""
        config_data = {
            "min_delay": 60.0,
            "max_delay": 120.0,
            "max_concurrent": 5,
            "priority": "HIGH",
            "enabled": True
        }
        
        config = validate_engagement_config(config_data)
        assert config.min_delay == 60.0
        assert config.priority == "HIGH"
    
    def test_validate_engagement_config_failure(self):
        """Test failed engagement config validation."""
        invalid_config = {
            "min_delay": "invalid",  # Should be float
            "max_delay": 120.0
        }
        
        with pytest.raises(ValidationError):
            validate_engagement_config(invalid_config)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_schema_summary(self):
        """Test schema summary generation."""
        summary = get_schema_summary()
        
        assert "persona_schema" in summary
        assert "engagement_schema" in summary
        
        persona_info = summary["persona_schema"]
        assert "required_fields" in persona_info
        assert "tone" in persona_info["required_fields"]
        assert "argument_chance" in persona_info["required_fields"]
        
        engagement_info = summary["engagement_schema"]
        assert "required_fields" in engagement_info
        assert "min_delay" in engagement_info["required_fields"]
        assert "priority_levels" in engagement_info 