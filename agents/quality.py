"""
Quality validation for Eliza swarm posts.
Ensures posts meet quality standards before posting.
"""

import re
from typing import Dict, List, Tuple


def validate(text: str, agent_name: str = None) -> Tuple[bool, List[str]]:
    """
    Validate post quality.
    
    Args:
        text: Post text to validate
        agent_name: Name of the agent (for persona-specific rules)
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Length check (140-240 characters)
    if len(text) < 140:
        issues.append(f"Post too short: {len(text)} chars (min 140)")
    elif len(text) > 240:
        issues.append(f"Post too long: {len(text)} chars (max 240)")
    
    # Must contain $BITCOIN or similar
    if not re.search(r'\$[A-Z]+', text):
        issues.append("Missing cryptocurrency ticker (e.g., $BITCOIN)")
    
    # Must contain at least one hashtag
    if not re.search(r'#[A-Za-z0-9_]+', text):
        issues.append("Missing hashtag")
    
    # Must contain #HarryPotterObamaSonic10Inu or similar
    if not re.search(r'#HarryPotterObamaSonic10Inu|#HPOS10I', text):
        issues.append("Missing required hashtag (#HarryPotterObamaSonic10Inu or #HPOS10I)")
    
    # Must contain at least one emoji
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
    )
    if not emoji_pattern.search(text):
        issues.append("Missing emoji")
    
    # Check for excessive caps (more than 50% of words)
    words = text.split()
    if words:
        caps_words = sum(1 for word in words if word.isupper() and len(word) > 1)
        if caps_words / len(words) > 0.5:
            issues.append("Too many ALL CAPS words")
    
    # Check for spam indicators (with AlphaScry exceptions)
    spam_indicators = ['FREE', 'WIN', 'GIVEAWAY', 'AIRDROP', '1000X', 'MOONSHOT', 'PRIZE', 'CONTEST', 'LOTTERY']
    alpha_allowed = ['ALPHA', 'SIGNAL', 'ALERT']  # Allow AlphaScry keywords
    
    if agent_name == "AlphaScry":
        # For AlphaScry, only check non-allowed spam indicators
        filtered_indicators = [ind for ind in spam_indicators if ind not in alpha_allowed]
        for indicator in filtered_indicators:
            if indicator in text.upper():
                print(f"DEBUG: AlphaScry spam trigger: '{indicator}' in text: {text}")
                issues.append("Contains spam indicators")
                break
    else:
        # For other agents, check all spam indicators
        for indicator in spam_indicators:
            if indicator in text.upper():
                print(f"DEBUG: {agent_name} spam trigger: '{indicator}' in text: {text}")
                issues.append("Contains spam indicators")
                break
    
    return len(issues) == 0, issues


def validate_reply(text: str, agent_name: str = None) -> Tuple[bool, List[str]]:
    """
    Validate reply quality (shorter length requirements).
    
    Args:
        text: Reply text to validate
        agent_name: Name of the agent (for persona-specific rules)
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Length check for replies (≤150 characters)
    if len(text) > 150:
        issues.append(f"Reply too long: {len(text)} chars (max 150)")
    
    # Must contain $BITCOIN or similar
    if not re.search(r'\$[A-Z]+', text):
        issues.append("Missing cryptocurrency ticker (e.g., $BITCOIN)")
    
    # Must contain at least one hashtag
    if not re.search(r'#[A-Za-z0-9_]+', text):
        issues.append("Missing hashtag")
    
    # Must contain #HarryPotterObamaSonic10Inu or similar
    if not re.search(r'#HarryPotterObamaSonic10Inu|#HPOS10I', text):
        issues.append("Missing required hashtag (#HarryPotterObamaSonic10Inu or #HPOS10I)")
    
    # Must contain at least one emoji
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
    )
    if not emoji_pattern.search(text):
        issues.append("Missing emoji")
    
    # Check for spam indicators (with AlphaScry exceptions)
    spam_indicators = ['FREE', 'WIN', 'GIVEAWAY', 'AIRDROP', '1000X', 'MOONSHOT', 'PRIZE', 'CONTEST', 'LOTTERY']
    alpha_allowed = ['ALPHA', 'SIGNAL', 'ALERT']  # Allow AlphaScry keywords
    
    if agent_name == "AlphaScry":
        # For AlphaScry, only check non-allowed spam indicators
        filtered_indicators = [ind for ind in spam_indicators if ind not in alpha_allowed]
        for indicator in filtered_indicators:
            if indicator in text.upper():
                print(f"DEBUG: AlphaScry spam trigger: '{indicator}' in text: {text}")
                issues.append("Contains spam indicators")
                break
    else:
        # For other agents, check all spam indicators
        for indicator in spam_indicators:
            if indicator in text.upper():
                print(f"DEBUG: {agent_name} spam trigger: '{indicator}' in text: {text}")
                issues.append("Contains spam indicators")
                break
    
    return len(issues) == 0, issues


def get_quality_score(text: str) -> float:
    """
    Get a quality score from 0.0 to 1.0.
    
    Args:
        text: Post text to score
        
    Returns:
        Quality score (0.0 = poor, 1.0 = excellent)
    """
    score = 1.0
    
    # Length score (optimal 180-200 chars)
    length = len(text)
    if 180 <= length <= 200:
        score += 0.1
    elif length < 140 or length > 240:
        score -= 0.3
    elif length < 160 or length > 220:
        score -= 0.1
    
    # Hashtag count (optimal 1-3)
    hashtag_count = len(re.findall(r'#[A-Za-z0-9_]+', text))
    if 1 <= hashtag_count <= 3:
        score += 0.1
    elif hashtag_count > 5:
        score -= 0.2
    
    # Emoji count (optimal 1-3)
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
    )
    emoji_count = len(emoji_pattern.findall(text))
    if 1 <= emoji_count <= 3:
        score += 0.1
    elif emoji_count > 5:
        score -= 0.1
    
    # Mention score (bonus for cross-engagement)
    if re.search(r'@[A-Za-z0-9_]+', text):
        score += 0.1
    
    # Crypto ticker score
    if re.search(r'\$[A-Z]+', text):
        score += 0.1
    
    return max(0.0, min(1.0, score))


def suggest_improvements(text: str) -> List[str]:
    """
    Suggest improvements for a post.
    
    Args:
        text: Post text to analyze
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    # Length suggestions
    length = len(text)
    if length < 140:
        suggestions.append("Add more content to reach minimum 140 characters")
    elif length > 240:
        suggestions.append("Shorten post to fit within 240 character limit")
    
    # Missing elements
    if not re.search(r'\$[A-Z]+', text):
        suggestions.append("Add a cryptocurrency ticker (e.g., $BITCOIN)")
    
    if not re.search(r'#[A-Za-z0-9_]+', text):
        suggestions.append("Add relevant hashtags")
    
    if not re.search(r'#HarryPotterObamaSonic10Inu|#HPOS10I', text):
        suggestions.append("Include #HarryPotterObamaSonic10Inu or #HPOS10I hashtag")
    
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
    )
    if not emoji_pattern.search(text):
        suggestions.append("Add an emoji to increase engagement")
    
    # Engagement suggestions
    if not re.search(r'@[A-Za-z0-9_]+', text):
        suggestions.append("Consider mentioning another swarm member for cross-engagement")
    
    return suggestions 