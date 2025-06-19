"""
Persona Formatting Utilities

Provides functions for formatting threads and injecting persona-specific slang.
"""

import random
import re
from typing import List, Dict, Any, Optional


def render_thread(text_chunks: List[str], max_length: int = 280) -> List[str]:
    """
    Render a list of text chunks into a numbered thread format.
    
    Args:
        text_chunks: List of text strings to turn into a thread
        max_length: Maximum length per tweet (default 280)
    
    Returns:
        List of formatted thread tweets with numbering
    """
    if not text_chunks:
        return []
    
    # Filter out empty chunks
    chunks = [chunk.strip() for chunk in text_chunks if chunk.strip()]
    
    if len(chunks) == 1:
        # Single tweet, no thread numbering needed
        return chunks
    
    formatted_tweets = []
    total_tweets = len(chunks)
    
    for i, chunk in enumerate(chunks, 1):
        # Calculate space needed for numbering
        thread_suffix = f" 🧵{i}/{total_tweets}"
        available_length = max_length - len(thread_suffix)
        
        # Truncate chunk if needed
        if len(chunk) > available_length:
            chunk = chunk[:available_length-3] + "..."
        
        # Add thread numbering
        formatted_tweet = chunk + thread_suffix
        formatted_tweets.append(formatted_tweet)
    
    return formatted_tweets


def inject_slang(text: str, persona: Optional[Dict[str, Any]] = None) -> str:
    """
    Inject persona-specific slang and style markers into text.
    
    Args:
        text: Original text to enhance
        persona: Persona configuration dict with style_markers, voice_patterns, etc.
    
    Returns:
        Enhanced text with persona-specific style
    """
    if not persona:
        return text
    
    enhanced_text = text
    
    # Get style markers and patterns
    style_markers = persona.get("style_markers", [])
    voice_patterns = persona.get("voice_patterns", [])
    tone = persona.get("tone", "")
    
    # Apply tone-specific transformations
    if tone == "sarcastic meme-lord":
        enhanced_text = _apply_meme_lord_style(enhanced_text, style_markers)
    elif tone == "cryptic-sage":
        enhanced_text = _apply_sage_style(enhanced_text, voice_patterns)
    elif tone == "analytical-technical":
        enhanced_text = _apply_technical_style(enhanced_text, style_markers)
    elif tone == "chaotic-playful":
        enhanced_text = _apply_chaotic_style(enhanced_text, style_markers)
    elif tone == "data-driven":
        enhanced_text = _apply_data_style(enhanced_text, style_markers)
    
    # Inject random style markers
    if style_markers and random.random() < 0.3:  # 30% chance
        marker = random.choice(style_markers)
        if marker not in enhanced_text:
            # Add marker at the end if it's an emoji or short phrase
            if len(marker) <= 3 or marker.startswith(("#", "@", "$")):
                enhanced_text = enhanced_text.rstrip() + f" {marker}"
    
    return enhanced_text


def _apply_meme_lord_style(text: str, style_markers: List[str]) -> str:
    """Apply MemeLord-specific styling."""
    # Convert to lowercase for meme lord style
    if any(marker == "all-lowercase" for marker in style_markers):
        # Keep crypto symbols uppercase
        words = text.split()
        processed_words = []
        for word in words:
            if word.startswith("$") or word.startswith("#"):
                processed_words.append(word)  # Keep crypto symbols as-is
            else:
                processed_words.append(word.lower())
        text = " ".join(processed_words)
    
    # Add meme expressions
    meme_additions = ["probably nothing", "this is fine", "few understand"]
    if random.random() < 0.2:  # 20% chance
        addition = random.choice(meme_additions)
        text = f"{text}\n\n{addition}"
    
    return text


def _apply_sage_style(text: str, voice_patterns: List[str]) -> str:
    """Apply LoreMaster sage styling."""
    # Occasionally prefix with wisdom phrases
    if voice_patterns and random.random() < 0.4:  # 40% chance
        prefix = random.choice(voice_patterns)
        if not text.lower().startswith(prefix.lower()[:10]):  # Avoid duplicates
            text = f"{prefix} {text}"
    
    return text


def _apply_technical_style(text: str, style_markers: List[str]) -> str:
    """Apply AlphaScry technical styling."""
    # Add technical prefixes
    tech_prefixes = ["Based on the data...", "Technical analysis shows...", "Key observations:"]
    if random.random() < 0.3:  # 30% chance
        prefix = random.choice(tech_prefixes)
        if not any(text.startswith(p) for p in tech_prefixes):
            text = f"{prefix} {text}"
    
    return text


def _apply_chaotic_style(text: str, style_markers: List[str]) -> str:
    """Apply GremlinGM chaotic styling."""
    # Add chaos markers
    chaos_additions = ["plot twist:", "chaos mode activated", "breaking: pure chaos"]
    if random.random() < 0.25:  # 25% chance
        addition = random.choice(chaos_additions)
        text = f"{addition} {text}"
    
    return text


def _apply_data_style(text: str, style_markers: List[str]) -> str:
    """Apply Agent2 data-driven styling."""
    # Ensure data markers are present
    data_markers = ["📊", "📈", "📉", "UPDATE:", "ALERT:"]
    
    # Check if already has data markers
    has_marker = any(marker in text for marker in data_markers)
    
    if not has_marker and random.random() < 0.6:  # 60% chance
        marker = random.choice(data_markers)
        text = f"{marker} {text}"
    
    return text


def format_price_update(btc_price: float, hpo_price: float, persona: Optional[Dict[str, Any]] = None) -> str:
    """
    Format a price update based on persona style.
    
    Args:
        btc_price: Bitcoin price
        hpo_price: HPO token price
        persona: Persona configuration
    
    Returns:
        Formatted price update text
    """
    if not persona:
        return f"$BITCOIN: ${btc_price:,.2f} | $HPOS10I: ${hpo_price:.6f}"
    
    tone = persona.get("tone", "")
    
    if tone == "data-driven":
        return f"📊 PRICE UPDATE: $BITCOIN ${btc_price:,.2f} | $HPOS10I ${hpo_price:.6f}"
    elif tone == "sarcastic meme-lord":
        diff_pct = ((hpo_price / btc_price) * 100) if btc_price > 0 else 0
        return f"bitcoin vs bitcoin's little brother: ${btc_price:,.0f} vs ${hpo_price:.6f} ({diff_pct:.2f}x difference) 🚀"
    elif tone == "cryptic-sage":
        return f"The scrolls record: $BITCOIN at ${btc_price:,.2f}, whilst #HarryPotterObamaSonic10Inu dances at ${hpo_price:.6f} 📜"
    elif tone == "analytical-technical":
        ratio = btc_price / hpo_price if hpo_price > 0 else 0
        return f"📈 Market analysis: $BITCOIN ${btc_price:,.2f} | $HPOS10I ${hpo_price:.6f} | Ratio: {ratio:,.0f}:1"
    elif tone == "chaotic-playful":
        return f"🎲 The cosmic scales tip: $BITCOIN ${btc_price:,.2f} ⚡ $HPOS10I ${hpo_price:.6f} 🔥"
    
    return f"$BITCOIN: ${btc_price:,.2f} | $HPOS10I: ${hpo_price:.6f}"


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    return re.findall(r'@(\w+)', text)


def extract_crypto_symbols(text: str) -> List[str]:
    """Extract $SYMBOL patterns from text."""
    return re.findall(r'\$([A-Z]{2,10})', text)


def count_emojis(text: str) -> int:
    """Count emoji characters in text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002700-\U000027BF"  # dingbats
        "\U0001f926-\U0001f937"  # additional emoticons
        "\U00010000-\U0010ffff"  # supplementary symbols
        "\u2640-\u2642"          # gender symbols
        "\u2600-\u2B55"          # misc symbols
        "\u200d"                 # zero width joiner
        "\u23cf"                 # eject symbol
        "\u23e9"                 # fast forward
        "\u231a"                 # watch
        "\ufe0f"                 # variation selector
        "\u3030"                 # wavy dash
        "]+"
    )
    
    emoji_matches = emoji_pattern.findall(text)
    return len(emoji_matches) 