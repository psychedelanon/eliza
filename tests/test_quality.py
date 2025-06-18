"""
Tests for quality validation module.
"""

import pytest
from agents.quality import validate, get_quality_score, suggest_improvements


class TestQualityValidation:
    """Test quality validation functions."""
    
    def test_validate_good_post(self):
        """Test that a good post passes validation."""
        good_post = "🔮 The ancient scrolls speak of $BITCOIN's rise @LoreMaster #HarryPotterObamaSonic10Inu"
        is_valid, issues = validate(good_post)
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_too_short(self):
        """Test that short posts fail validation."""
        short_post = "Short post"
        is_valid, issues = validate(short_post)
        assert not is_valid
        assert any("too short" in issue for issue in issues)
    
    def test_validate_too_long(self):
        """Test that long posts fail validation."""
        long_post = "x" * 250
        is_valid, issues = validate(long_post)
        assert not is_valid
        assert any("too long" in issue for issue in issues)
    
    def test_validate_missing_ticker(self):
        """Test that posts without crypto ticker fail validation."""
        post = "This is a post without any cryptocurrency ticker #HarryPotterObamaSonic10Inu 🔮"
        is_valid, issues = validate(post)
        assert not is_valid
        assert any("Missing cryptocurrency ticker" in issue for issue in issues)
    
    def test_validate_missing_hashtag(self):
        """Test that posts without hashtags fail validation."""
        post = "This is a post without hashtags $BITCOIN 🔮"
        is_valid, issues = validate(post)
        assert not is_valid
        assert any("Missing hashtag" in issue for issue in issues)
    
    def test_validate_missing_required_hashtag(self):
        """Test that posts without required hashtag fail validation."""
        post = "This post has a hashtag but not the required one $BITCOIN 🔮 #Crypto"
        is_valid, issues = validate(post)
        assert not is_valid
        assert any("Missing required hashtag" in issue for issue in issues)
    
    def test_validate_missing_emoji(self):
        """Test that posts without emojis fail validation."""
        post = "This post has no emoji but includes $BITCOIN and #HarryPotterObamaSonic10Inu"
        is_valid, issues = validate(post)
        assert not is_valid
        assert any("Missing emoji" in issue for issue in issues)
    
    def test_validate_excessive_caps(self):
        """Test that posts with excessive caps fail validation."""
        post = "THIS POST HAS TOO MANY ALL CAPS WORDS $BITCOIN #HarryPotterObamaSonic10Inu 🔮"
        is_valid, issues = validate(post)
        assert not is_valid
        assert any("Too many ALL CAPS words" in issue for issue in issues)
    
    def test_validate_spam_indicators(self):
        """Test that posts with spam indicators fail validation."""
        post = "FREE GIVEAWAY WIN $BITCOIN #HarryPotterObamaSonic10Inu 🔮"
        is_valid, issues = validate(post)
        assert not is_valid
        assert any("Contains spam indicators" in issue for issue in issues)
    
    def test_validate_multiple_issues(self):
        """Test that multiple issues are reported."""
        bad_post = "Short"
        is_valid, issues = validate(bad_post)
        assert not is_valid
        assert len(issues) > 1  # Should have multiple issues


class TestQualityScore:
    """Test quality scoring functions."""
    
    def test_quality_score_perfect_post(self):
        """Test that a perfect post gets high score."""
        perfect_post = "🔮 The ancient scrolls speak of $BITCOIN's rise @LoreMaster #HarryPotterObamaSonic10Inu"
        score = get_quality_score(perfect_post)
        assert score >= 1.0
    
    def test_quality_score_optimal_length(self):
        """Test that optimal length posts get bonus points."""
        optimal_post = "x" * 190 + " $BITCOIN #HarryPotterObamaSonic10Inu 🔮"
        score = get_quality_score(optimal_post)
        assert score > 1.0
    
    def test_quality_score_too_short(self):
        """Test that short posts get penalized."""
        short_post = "Short $BITCOIN #HarryPotterObamaSonic10Inu 🔮"
        score = get_quality_score(short_post)
        assert score < 1.0
    
    def test_quality_score_too_long(self):
        """Test that long posts get penalized."""
        long_post = "x" * 250 + " $BITCOIN #HarryPotterObamaSonic10Inu 🔮"
        score = get_quality_score(long_post)
        assert score < 1.0
    
    def test_quality_score_optimal_hashtags(self):
        """Test that optimal hashtag count gets bonus points."""
        good_post = "🔮 The ancient scrolls speak of $BITCOIN's rise #HarryPotterObamaSonic10Inu #CryptoLore"
        score = get_quality_score(good_post)
        assert score >= 1.0
    
    def test_quality_score_too_many_hashtags(self):
        """Test that too many hashtags get penalized."""
        hashtag_spam = "🔮 $BITCOIN #HarryPotterObamaSonic10Inu #Crypto #BTC #Bitcoin #CryptoLore #WAGMI #HODL"
        score = get_quality_score(hashtag_spam)
        assert score < 1.0
    
    def test_quality_score_mention_bonus(self):
        """Test that mentions get bonus points."""
        post_with_mention = "🔮 The ancient scrolls speak of $BITCOIN's rise @LoreMaster #HarryPotterObamaSonic10Inu"
        post_without_mention = "🔮 The ancient scrolls speak of $BITCOIN's rise #HarryPotterObamaSonic10Inu"
        
        score_with = get_quality_score(post_with_mention)
        score_without = get_quality_score(post_without_mention)
        
        assert score_with > score_without


class TestSuggestImprovements:
    """Test improvement suggestion functions."""
    
    def test_suggest_improvements_short_post(self):
        """Test suggestions for short posts."""
        short_post = "Short"
        suggestions = suggest_improvements(short_post)
        assert any("Add more content" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_long_post(self):
        """Test suggestions for long posts."""
        long_post = "x" * 250
        suggestions = suggest_improvements(long_post)
        assert any("Shorten post" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_missing_ticker(self):
        """Test suggestions for missing ticker."""
        post = "This post has no ticker #HarryPotterObamaSonic10Inu 🔮"
        suggestions = suggest_improvements(post)
        assert any("Add a cryptocurrency ticker" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_missing_hashtag(self):
        """Test suggestions for missing hashtag."""
        post = "This post has no hashtag $BITCOIN 🔮"
        suggestions = suggest_improvements(post)
        assert any("Add relevant hashtags" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_missing_required_hashtag(self):
        """Test suggestions for missing required hashtag."""
        post = "This post has hashtag but not required one $BITCOIN 🔮 #Crypto"
        suggestions = suggest_improvements(post)
        assert any("Include #HarryPotterObamaSonic10Inu" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_missing_emoji(self):
        """Test suggestions for missing emoji."""
        post = "This post has no emoji $BITCOIN #HarryPotterObamaSonic10Inu"
        suggestions = suggest_improvements(post)
        assert any("Add an emoji" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_missing_mention(self):
        """Test suggestions for missing mention."""
        post = "This post has no mention $BITCOIN #HarryPotterObamaSonic10Inu 🔮"
        suggestions = suggest_improvements(post)
        assert any("Consider mentioning another swarm member" in suggestion for suggestion in suggestions)
    
    def test_suggest_improvements_perfect_post(self):
        """Test that perfect posts get no suggestions."""
        perfect_post = "🔮 The ancient scrolls speak of $BITCOIN's rise @LoreMaster #HarryPotterObamaSonic10Inu"
        suggestions = suggest_improvements(perfect_post)
        assert len(suggestions) == 0


class TestQualityIntegration:
    """Test quality validation integration with real posts."""
    
    def test_loremaster_style_post(self):
        """Test a LoreMaster style post."""
        post = "🔮 The ancient scrolls speak of $BITCOIN's rise @LoreMaster #HarryPotterObamaSonic10Inu"
        is_valid, issues = validate(post)
        score = get_quality_score(post)
        suggestions = suggest_improvements(post)
        
        assert is_valid
        assert score >= 1.0
        assert len(suggestions) == 0
    
    def test_memelord_style_post(self):
        """Test a MemeLord style post."""
        post = "🚀 Diamond hands meet $BITCOIN magic @MemeLord #HarryPotterObamaSonic10Inu 💎"
        is_valid, issues = validate(post)
        score = get_quality_score(post)
        suggestions = suggest_improvements(post)
        
        assert is_valid
        assert score >= 1.0
        assert len(suggestions) == 0
    
    def test_alphascy_style_post(self):
        """Test an AlphaScry style post."""
        post = "🔍 Alpha alert: $BITCOIN showing strength @AlphaScry #HarryPotterObamaSonic10Inu 📊"
        is_valid, issues = validate(post)
        score = get_quality_score(post)
        suggestions = suggest_improvements(post)
        
        assert is_valid
        assert score >= 1.0
        assert len(suggestions) == 0
    
    def test_gremlingm_style_post(self):
        """Test a GremlinGM style post."""
        post = "🎮 Chaos magic flows through $BITCOIN @GremlinGM #HarryPotterObamaSonic10Inu 🔥"
        is_valid, issues = validate(post)
        score = get_quality_score(post)
        suggestions = suggest_improvements(post)
        
        assert is_valid
        assert score >= 1.0
        assert len(suggestions) == 0 