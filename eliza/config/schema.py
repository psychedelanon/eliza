"""
Configuration Schema Validation

Pydantic models for validating persona and engagement configuration files.
Ensures all YAML files have required keys and valid values.
"""

import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, validator, ValidationError

log = logging.getLogger("config_schema")


class FormatConfig(BaseModel):
    """Configuration for content format options."""
    type: Literal["single", "thread", "meme_image", "poll"] = Field(
        ..., description="Type of content format"
    )
    max_tweets: Optional[int] = Field(
        None, ge=1, le=10, description="Maximum tweets for thread format"
    )
    probability: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Probability of using this format"
    )


class PersonaSchema(BaseModel):
    """Schema for agent persona configuration."""
    
    tone: str = Field(..., description="Agent's conversational tone")
    
    style_markers: List[str] = Field(
        ..., min_items=1, description="List of style markers and phrases"
    )
    
    formats: List[FormatConfig] = Field(
        ..., min_items=1, description="Supported content formats"
    )
    
    allowed_refs: Optional[List[str]] = Field(
        default=[], description="Allowed references and mentions"
    )
    
    voice_patterns: Optional[List[str]] = Field(
        default=[], description="Common voice patterns and phrases"
    )
    
    argument_chance: float = Field(
        ..., ge=0.0, le=1.0, description="Probability of triggering arguments"
    )
    
    topic_preferences: Optional[List[str]] = Field(
        default=[], description="Preferred discussion topics"
    )
    
    engagement_style: Optional[List[str]] = Field(
        default=[], description="Engagement behavior patterns"
    )
    
    @validator('tone')
    def validate_tone(cls, v):
        """Validate tone is non-empty."""
        if not v.strip():
            raise ValueError("Tone cannot be empty")
        return v.strip()
    
    @validator('style_markers')
    def validate_style_markers(cls, v):
        """Validate style markers are non-empty."""
        cleaned = [marker.strip() for marker in v if marker.strip()]
        if not cleaned:
            raise ValueError("At least one style marker is required")
        return cleaned
    
    @validator('formats')
    def validate_formats(cls, v):
        """Validate format probabilities sum to reasonable value."""
        if not v:
            raise ValueError("At least one format is required")
        
        # Check probabilities sum to <= 1.0 if they exist
        total_prob = sum(fmt.probability for fmt in v if fmt.probability is not None)
        if total_prob > 1.0:
            raise ValueError(f"Format probabilities sum to {total_prob}, must be <= 1.0")
        
        return v


class EngagementConfigSchema(BaseModel):
    """Schema for engagement behavior configuration."""
    
    min_delay: float = Field(
        ..., ge=0.0, description="Minimum delay before engagement (seconds)"
    )
    
    max_delay: float = Field(
        ..., ge=0.0, description="Maximum delay before engagement (seconds)"
    )
    
    max_concurrent: int = Field(
        default=3, ge=1, le=10, description="Maximum concurrent engagements"
    )
    
    priority: Literal["LOW", "NORMAL", "HIGH", "CRITICAL"] = Field(
        default="NORMAL", description="Event priority level"
    )
    
    enabled: bool = Field(
        default=True, description="Whether engagement is enabled"
    )
    
    @validator('max_delay')
    def validate_delay_range(cls, v, values):
        """Ensure max_delay >= min_delay."""
        if 'min_delay' in values and v < values['min_delay']:
            raise ValueError("max_delay must be >= min_delay")
        return v


def validate_persona_file(file_path: Path) -> PersonaSchema:
    """
    Validate a single persona YAML file.
    
    Args:
        file_path: Path to the persona YAML file
        
    Returns:
        Validated PersonaSchema instance
        
    Raises:
        ValidationError: If the file doesn't match the schema
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file isn't valid YAML
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Persona file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}")
    
    if data is None:
        raise ValidationError(f"Empty YAML file: {file_path}", PersonaSchema)
    
    try:
        persona = PersonaSchema(**data)
        log.info(f"✅ Validated persona file: {file_path.name}")
        return persona
    except ValidationError as e:
        log.error(f"❌ Validation failed for {file_path.name}: {e}")
        raise


def validate_all_personas(persona_dir: Optional[Path] = None) -> Dict[str, PersonaSchema]:
    """
    Validate all persona files in the persona directory.
    
    Args:
        persona_dir: Path to persona directory (defaults to ./persona)
        
    Returns:
        Dictionary mapping agent names to validated PersonaSchema instances
        
    Raises:
        ValidationError: If any file fails validation
    """
    if persona_dir is None:
        persona_dir = Path("persona")
    
    if not persona_dir.exists():
        raise FileNotFoundError(f"Persona directory not found: {persona_dir}")
    
    personas = {}
    errors = []
    
    # Find all agent YAML files
    agent_files = list(persona_dir.glob("agent*.yml"))
    
    if not agent_files:
        raise FileNotFoundError(f"No agent*.yml files found in {persona_dir}")
    
    for file_path in sorted(agent_files):
        try:
            persona = validate_persona_file(file_path)
            agent_name = file_path.stem  # e.g., "agent1" from "agent1.yml"
            personas[agent_name] = persona
        except (ValidationError, yaml.YAMLError, FileNotFoundError) as e:
            errors.append(f"{file_path.name}: {e}")
    
    if errors:
        error_msg = "Persona validation failed:\n" + "\n".join(errors)
        raise ValidationError(error_msg, PersonaSchema)
    
    log.info(f"✅ Validated {len(personas)} persona files successfully")
    return personas


def validate_engagement_config(config_data: Dict[str, Any]) -> EngagementConfigSchema:
    """
    Validate engagement configuration data.
    
    Args:
        config_data: Raw configuration dictionary
        
    Returns:
        Validated EngagementConfigSchema instance
        
    Raises:
        ValidationError: If the config doesn't match the schema
    """
    try:
        return EngagementConfigSchema(**config_data)
    except ValidationError as e:
        log.error(f"❌ Engagement config validation failed: {e}")
        raise


def get_schema_summary() -> Dict[str, Any]:
    """Get a summary of the configuration schema."""
    return {
        "persona_schema": {
            "required_fields": ["tone", "style_markers", "formats", "argument_chance"],
            "optional_fields": ["allowed_refs", "voice_patterns", "topic_preferences", "engagement_style"],
            "format_types": ["single", "thread", "meme_image", "poll"],
            "argument_chance_range": [0.0, 1.0]
        },
        "engagement_schema": {
            "required_fields": ["min_delay", "max_delay"],
            "optional_fields": ["max_concurrent", "priority", "enabled"],
            "priority_levels": ["LOW", "NORMAL", "HIGH", "CRITICAL"]
        }
    }


# CLI helper for validation
def main():
    """CLI entry point for schema validation."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate ElizaOS configuration files")
    parser.add_argument(
        "--persona-dir", 
        type=Path, 
        default=Path("persona"),
        help="Path to persona directory (default: ./persona)"
    )
    parser.add_argument(
        "--file", 
        type=Path,
        help="Validate a single persona file"
    )
    parser.add_argument(
        "--summary", 
        action="store_true",
        help="Show schema summary"
    )
    
    args = parser.parse_args()
    
    if args.summary:
        summary = get_schema_summary()
        print("📋 ElizaOS Configuration Schema Summary")
        print("=" * 50)
        for schema_name, schema_info in summary.items():
            print(f"\n{schema_name.upper()}:")
            for key, value in schema_info.items():
                print(f"  {key}: {value}")
        return
    
    try:
        if args.file:
            # Validate single file
            persona = validate_persona_file(args.file)
            print(f"✅ {args.file.name} is valid")
            print(f"   Tone: {persona.tone}")
            print(f"   Argument Chance: {persona.argument_chance}")
            print(f"   Formats: {len(persona.formats)}")
        else:
            # Validate all personas
            personas = validate_all_personas(args.persona_dir)
            print(f"✅ All {len(personas)} persona files are valid")
            for agent_name, persona in personas.items():
                print(f"   {agent_name}: {persona.tone} (args: {persona.argument_chance})")
                
    except (ValidationError, FileNotFoundError, yaml.YAMLError) as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 