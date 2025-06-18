"""
Smart post generator for Eliza swarm agents.
Generates high-quality, cross-amplifying content with proper hashtags and engagement.
"""

import random
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

from eliza import llm


@dataclass
class PersonaConfig:
    """Configuration for each persona's posting style."""
    name: str
    system_prompt: str
    hashtags: List[str]
    emoji_bank: List[str]
    engagement_style: str
    mention_probability: float = 0.5


# Persona configurations
PERSONA_CONFIGS = {
    "LoreMaster": PersonaConfig(
        name="LoreMaster",
        system_prompt=(
            "You are a mythic lore master chronicling the legends of $BITCOIN. "
            "Write in dramatic, mysterious tones with ancient wisdom. "
            "Reference prophecies, mystical forces, and the eternal struggle between light and dark. "
            "Keep posts 140-240 characters. Always include $BITCOIN and one hashtag from the pool."
        ),
        hashtags=["#HarryPotterObamaSonic10Inu", "#BITCOIN", "#CryptoLore", "#WizardMoney"],
        emoji_bank=["🔮", "⚡", "🌟", "🕯️", "📜", "🏰", "⚔️", "🛡️"],
        engagement_style="quote_tweet_20_reply_50_like_30"
    ),
    "MemeLord": PersonaConfig(
        name="MemeLord",
        system_prompt=(
            "You are the ultimate meme lord of crypto. "
            "Create viral, humorous content with pop culture references, puns, and absurdist humor. "
            "Use emojis liberally and reference trending memes. "
            "Keep posts 140-240 characters. Always include $BITCOIN and one hashtag from the pool."
        ),
        hashtags=["#HarryPotterObamaSonic10Inu", "#HPOS10I", "#CryptoMemes", "#WAGMI"],
        emoji_bank=["🚀", "💎", "🦍", "🌙", "🔥", "💯", "😂", "🤡", "🎭"],
        engagement_style="meme_reply_60_like_40"
    ),
    "AlphaScry": PersonaConfig(
        name="AlphaScry",
        system_prompt=(
            "You are an alpha scryer, revealing hidden market insights and prophetic trading wisdom. "
            "Write with urgency and insider knowledge. Use technical analysis terms and market psychology. "
            "Keep posts 140-240 characters. Always include $BITCOIN and one hashtag from the pool."
        ),
        hashtags=["#HarryPotterObamaSonic10Inu", "#Alpha", "#CryptoAlpha", "#Trading"],
        emoji_bank=["🔍", "📊", "📈", "🎯", "⚡", "💡", "🔮", "🎪"],
        engagement_style="thread_reply_70_quote_30"
    ),
    "GremlinGM": PersonaConfig(
        name="GremlinGM",
        system_prompt=(
            "You are a chaotic game master of the crypto realm. "
            "Create unpredictable, wild content with gaming references, chaos magic, and pure hype. "
            "Use gaming terminology and chaotic energy. "
            "Keep posts 140-240 characters. Always include $BITCOIN and one hashtag from the pool."
        ),
        hashtags=["#HarryPotterObamaSonic10Inu", "#GremlinGM", "#ChaosMagic", "#Gaming"],
        emoji_bank=["🎮", "🎲", "⚔️", "🔥", "💥", "🎪", "🎭", "🃏", "🎯"],
        engagement_style="chaos_reply_80_like_20"
    )
}

# Swarm member handles for cross-engagement
SWARM_HANDLES = ["@LoreMaster", "@MemeLord", "@AlphaScry", "@GremlinGM"]


def get_trending_tokens() -> List[str]:
    """Get trending tokens (stub implementation for dry-run)."""
    if os.getenv("DRY_RUN", "true").lower() == "true":
        return ["$PEPE", "$DOGE", "$SHIB", "$FLOKI"]
    # TODO: Integrate with CoinGecko API for real trending tokens
    return ["$BITCOIN", "$ETH", "$SOL", "$ADA"]


def compose_post(persona_name: str, event: Optional[Dict] = None, dry_run: bool = True) -> str:
    """
    Compose a high-quality post for the given persona.
    
    Args:
        persona_name: Name of the persona (LoreMaster, MemeLord, etc.)
        event: Optional event data to include in the post
        dry_run: If True, return stub content without LLM call
    
    Returns:
        Composed post text (140-240 characters)
    """
    if persona_name not in PERSONA_CONFIGS:
        return f"{persona_name} default post about $BITCOIN #HarryPotterObamaSonic10Inu"
    
    config = PERSONA_CONFIGS[persona_name]
    
    if dry_run:
        # Return high-quality stub content for dry-run
        return _generate_stub_post(config, event)
    
    # Build ChatML prompt
    prompt = _build_prompt(config, event)
    
    # Call LLM
    response = llm.complete(
        prompt,
        temperature=0.8,
        max_tokens=100
    )
    
    # Post-process and validate
    post = _post_process(response, config)
    return _validate_and_trim(post, config)


def _generate_stub_post(config: PersonaConfig, event: Optional[Dict] = None) -> str:
    """Generate high-quality stub content for dry-run mode."""
    hashtag = random.choice(config.hashtags)
    emoji = random.choice(config.emoji_bank)
    mention = random.choice(SWARM_HANDLES) if random.random() < config.mention_probability else ""
    
    # Event-driven content
    if event and event.get("type") == "new_hot_token":
        symbol = event.get("symbol", "$XYZ")
        pct = event.get("pct", 100)
        base_content = f"🔥 {symbol} up {pct}% — are you watching?"
    else:
        # Persona-specific stub content
        base_content = _get_persona_stub_content(config.name)
    
    # Build final post
    post_parts = [base_content]
    if mention:
        post_parts.append(mention)
    post_parts.append(hashtag)
    
    post = f"{emoji} {' '.join(post_parts)}"
    return _validate_and_trim(post, config)


def _get_persona_stub_content(persona_name: str) -> str:
    """Get persona-specific stub content."""
    stub_content = {
        "LoreMaster": [
            "The ancient scrolls speak of $BITCOIN's rise, foretelling a time when digital gold shall rule the realm of finance. The mystical forces align as we witness the prophecy unfold before our very eyes.",
            "A prophecy foretold this $BITCOIN moment centuries ago, when the wise ones spoke of a currency that would transcend borders and unite the world in financial freedom.",
            "The mystical forces align for $BITCOIN as the ancient ones predicted. In the depths of time, this moment was destined to come, and now we stand witness to the greatest financial revolution in human history.",
            "In the depths of time, $BITCOIN was destined to rise from the digital realm and challenge the very foundations of traditional finance. The ancient scrolls never lie."
        ],
        "MemeLord": [
            "Diamond hands meet $BITCOIN magic in the most epic crossover of all time! When the memes align with the charts, we all become legends of the crypto realm. This is the way!",
            "When $BITCOIN moons, we all become legends of the digital age. The prophecy is real, the memes are stronger than ever, and WAGMI energy flows through every hodler's veins.",
            "The $BITCOIN prophecy is real, and the memes are the key to understanding the future of finance. When diamond hands meet digital gold, magic happens in the crypto universe.",
            "WAGMI with $BITCOIN energy flowing through every transaction. The memes predicted this moment, and now we're living in the golden age of decentralized finance."
        ],
        "AlphaScry": [
            "Alpha alert: $BITCOIN showing strength that the charts have been predicting for weeks. Market psychology favors the patient, and insider knowledge reveals this is just the beginning of the bull run.",
            "The charts reveal $BITCOIN's path to financial dominance, with technical analysis confirming what the alpha hunters have been whispering about. This is the accumulation phase before the explosion.",
            "Insider knowledge: $BITCOIN primed for a major breakout as institutional money flows into the digital asset space. Market psychology and technical indicators align perfectly.",
            "Market psychology favors $BITCOIN as the smart money recognizes the value proposition. The alpha is clear: this is the future of money, and we're early to the party."
        ],
        "GremlinGM": [
            "Chaos magic flows through $BITCOIN as the game master calls forth the greatest financial revolution in gaming history. Roll for initiative, because the crypto realm is about to explode!",
            "The game master calls: $BITCOIN rises from the depths of the digital dungeon to challenge the very fabric of traditional finance. Critical hit on the old system!",
            "Roll for $BITCOIN initiative as chaos magic transforms the financial landscape. The game master has spoken, and the dice of destiny favor the brave crypto adventurers.",
            "Critical hit on $BITCOIN charts as the game master unleashes the power of decentralized finance. The chaos magic is real, and the gaming community leads the revolution."
        ]
    }
    return random.choice(stub_content.get(persona_name, ["$BITCOIN is the way of the future, and we're all part of this incredible journey."]))


def _build_prompt(config: PersonaConfig, event: Optional[Dict] = None) -> str:
    """Build ChatML prompt for LLM."""
    prompt_parts = [config.system_prompt]
    
    # Add event context if available
    if event:
        if event.get("type") == "new_hot_token":
            symbol = event.get("symbol", "$XYZ")
            pct = event.get("pct", 100)
            prompt_parts.append(f"Current event: {symbol} is up {pct}%. Include this in your post.")
    
    # Add hashtag and emoji guidance
    hashtags_str = ", ".join(config.hashtags)
    emojis_str = ", ".join(config.emoji_bank)
    prompt_parts.append(f"Use hashtags from: {hashtags_str}")
    prompt_parts.append(f"Use emojis from: {emojis_str}")
    
    # Add mention guidance
    if random.random() < config.mention_probability:
        mention = random.choice(SWARM_HANDLES)
        prompt_parts.append(f"Mention {mention} in your post.")
    
    return "\n".join(prompt_parts)


def _post_process(text: str, config: PersonaConfig) -> str:
    """Post-process LLM response."""
    # Clean up the response
    text = text.strip()
    
    # Ensure hashtag is present
    if not any(hashtag in text for hashtag in config.hashtags):
        text += f" {random.choice(config.hashtags)}"
    
    # Ensure emoji is present
    if not any(emoji in text for emoji in config.emoji_bank):
        text = f"{random.choice(config.emoji_bank)} {text}"
    
    return text


def _validate_and_trim(text: str, config: PersonaConfig) -> str:
    """Validate and trim text to 240 characters while ensuring all required elements."""
    # Ensure $BITCOIN is mentioned
    if "$BITCOIN" not in text:
        text = f"$BITCOIN {text}"
    
    # Ensure required hashtag is present
    if "#HarryPotterObamaSonic10Inu" not in text and "#HPOS10I" not in text:
        text += " #HarryPotterObamaSonic10Inu"
    
    # Ensure at least one emoji is present
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
    )
    if not emoji_pattern.search(text):
        emoji = random.choice(config.emoji_bank)
        text = f"{emoji} {text}"
    
    # Ensure minimum length (140 chars)
    if len(text) < 140:
        # Add more content to reach minimum length
        additional_content = [
            " The future is now.",
            " This is just the beginning.",
            " The revolution continues.",
            " We're witnessing history.",
            " The prophecy unfolds.",
            " Magic is real.",
            " The game has changed.",
            " This is the way."
        ]
        while len(text) < 140:
            text += random.choice(additional_content)
    
    # Trim to 240 characters
    if len(text) > 240:
        text = text[:237] + "..."
    
    return text


def get_engagement_weights(persona_name: str) -> Dict[str, float]:
    """Get engagement action weights for a persona."""
    if persona_name not in PERSONA_CONFIGS:
        return {"like": 0.5, "reply": 0.3, "quote": 0.2}
    
    config = PERSONA_CONFIGS[persona_name]
    style = config.engagement_style
    
    if "quote_tweet_20_reply_50_like_30" in style:
        return {"quote": 0.2, "reply": 0.5, "like": 0.3}
    elif "meme_reply_60_like_40" in style:
        return {"reply": 0.6, "like": 0.4}
    elif "thread_reply_70_quote_30" in style:
        return {"reply": 0.7, "quote": 0.3}
    elif "chaos_reply_80_like_20" in style:
        return {"reply": 0.8, "like": 0.2}
    else:
        return {"like": 0.5, "reply": 0.3, "quote": 0.2}


def compose_reply(persona_name: str, base_text: str, event: Optional[Dict] = None, dry_run: bool = True) -> str:
    """
    Compose a high-quality reply for the given persona.
    
    Args:
        persona_name: Name of the persona (LoreMaster, MemeLord, etc.)
        base_text: Base text to build reply from
        event: Optional event data to include in the reply
        dry_run: If True, return stub content without LLM call
    
    Returns:
        Composed reply text (≤150 characters)
    """
    if persona_name not in PERSONA_CONFIGS:
        return f"$BITCOIN is the way #HarryPotterObamaSonic10Inu"
    
    config = PERSONA_CONFIGS[persona_name]
    
    if dry_run:
        # Return high-quality stub reply for dry-run
        return _generate_stub_reply(config, base_text, event)
    
    # Build ChatML prompt for reply
    prompt = _build_reply_prompt(config, base_text, event)
    
    # Call LLM
    response = llm.complete(
        prompt,
        temperature=0.8,
        max_tokens=80
    )
    
    # Post-process and validate
    reply = _post_process_reply(response, config)
    return _validate_and_trim_reply(reply, config)


def _generate_stub_reply(config: PersonaConfig, base_text: str, event: Optional[Dict] = None) -> str:
    """Generate high-quality stub reply for dry-run mode."""
    hashtag = random.choice(config.hashtags)
    emoji = random.choice(config.emoji_bank)
    
    # Event-driven reply content
    if event and event.get("type") == "price_post":
        btc = event.get("btc", 0)
        hpo = event.get("hpo", 0)
        if btc > 0 and hpo > 0:
            diff_pct = ((hpo - btc) / btc) * 100
            base_content = f"The charts show a {diff_pct:+.2f}% swing"
        else:
            base_content = "The market speaks"
    else:
        # Persona-specific stub reply content
        base_content = _get_persona_stub_reply(config.name)
    
    # Build final reply
    reply = f"{emoji} {base_content} {hashtag}"
    return _validate_and_trim_reply(reply, config)


def _get_persona_stub_reply(persona_name: str) -> str:
    """Get persona-specific stub reply content."""
    stub_replies = {
        "LoreMaster": [
            "The ancient scrolls speak",
            "A prophecy foretold this",
            "The mystical forces align",
            "In the depths of time"
        ],
        "MemeLord": [
            "Diamond hands energy",
            "This is the way",
            "WAGMI vibes detected",
            "The prophecy is real"
        ],
        "AlphaScry": [
            "Alpha detected",
            "The charts confirm",
            "Insider knowledge",
            "Market psychology favors"
        ],
        "GremlinGM": [
            "Chaos magic flows",
            "The game master calls",
            "Critical hit detected",
            "Roll for initiative"
        ]
    }
    return random.choice(stub_replies.get(persona_name, ["The way is clear"]))


def _build_reply_prompt(config: PersonaConfig, base_text: str, event: Optional[Dict] = None) -> str:
    """Build ChatML prompt for reply generation."""
    prompt_parts = [
        f"You are {config.name}. Reply to this tweet in your unique style:",
        f"Original tweet: {base_text}",
        config.system_prompt.replace("Keep posts 140-240 characters", "Keep reply under 150 characters")
    ]
    
    # Add event context if available
    if event:
        if event.get("type") == "price_post":
            btc = event.get("btc", 0)
            hpo = event.get("hpo", 0)
            prompt_parts.append(f"Price data: BTC=${btc}, HPO=${hpo}")
    
    # Add hashtag and emoji guidance
    hashtags_str = ", ".join(config.hashtags)
    emojis_str = ", ".join(config.emoji_bank)
    prompt_parts.append(f"Use hashtags from: {hashtags_str}")
    prompt_parts.append(f"Use emojis from: {emojis_str}")
    
    return "\n".join(prompt_parts)


def _post_process_reply(text: str, config: PersonaConfig) -> str:
    """Post-process LLM reply response."""
    # Clean up the response
    text = text.strip()
    
    # Ensure hashtag is present
    if not any(hashtag in text for hashtag in config.hashtags):
        text += f" {random.choice(config.hashtags)}"
    
    # Ensure emoji is present
    if not any(emoji in text for emoji in config.emoji_bank):
        text = f"{random.choice(config.emoji_bank)} {text}"
    
    return text


def _validate_and_trim_reply(text: str, config: PersonaConfig) -> str:
    """Validate and trim reply text to 150 characters."""
    # Ensure $BITCOIN is mentioned
    if "$BITCOIN" not in text:
        text = f"$BITCOIN {text}"
    
    # Trim to 150 characters for replies
    if len(text) > 150:
        text = text[:147] + "..."
    
    return text 