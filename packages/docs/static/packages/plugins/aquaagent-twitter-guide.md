# AquaAgent Twitter Integration Guide

This guide covers enabling AquaAgent's personality and Twitter/X capabilities in ElizaOS.

## 1. Confirm the Persona

1. Open `src/index.ts` in your project and ensure the `character` object is named `AquaAgent` and includes your desired `system` prompt and `bio` traits.
2. Launch the ElizaOS dashboard (`bun run dev` or `elizaos dev`). In a new chat, AquaAgent should greet you in its custom style. If not, restart the server or check the logs for character loading errors.

## 2. Configure Twitter Access

AquaAgent supports two authentication methods.

### Method 1: Username/Password Login

Add these variables to your `.env`:

```env
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email
TWITTER_2FA_SECRET=your_2fa_secret   # optional
TWITTER_DRY_RUN=false                # true to simulate tweets
TWITTER_ENABLE_POST_GENERATION=true  # auto-generate tweets
TWITTER_POST_INTERVAL_MIN=60         # minutes between posts
TWITTER_POST_INTERVAL_MAX=180
TWITTER_INTERACTION_ENABLE=true      # reply to mentions
TWITTER_POLL_INTERVAL=120            # seconds
```

### Method 2: API Keys

Alternatively set the API credentials:

```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret
```

If both methods are present, login credentials take priority.

After editing the `.env`, restart the agent so the plugin loads with the new credentials.

## 3. Verify Tweeting

1. **Dry Run** – set `TWITTER_DRY_RUN=true` and start the agent. Check the console for messages like `TwitterClient.sendTweet – Would send tweet`. This confirms the plugin is active without posting.
2. **Live Test** – disable dry run and reduce the post interval. You can also instruct AquaAgent in chat to "tweet" something. Watch the logs for a tweet ID, then view the account on Twitter to confirm.
3. **Logs** – run with `DEBUG=eliza:*` for verbose output. Authentication or content errors will appear here.

## 4. Preparing for Automation

With the plugin verified, you can experiment with scheduled posts or additional plugins. Services such as the provided `scheduledTweetService.ts` handle periodic tweets and can be extended for more features.
