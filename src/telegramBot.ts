import { Telegraf } from 'telegraf';
import fetch from 'node-fetch';

export interface TelegramBotOptions {
  token: string;
  serverUrl?: string; // network server url
}

export function extractTweetId(text: string): string | null {
  const match = text.match(/status\/(\d+)/);
  return match ? match[1] : null;
}

export function createTelegramBot({ token, serverUrl = 'http://localhost:3000' }: TelegramBotOptions) {
  const bot = new Telegraf(token);

  bot.on('text', async (ctx) => {
    const text = ctx.message.text || '';
    const id = extractTweetId(text);
    if (!id) {
      await ctx.reply('Send a tweet URL');
      return;
    }
    try {
      await fetch(`${serverUrl}/coordinate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          targetPostId: id,
          engagementTypes: ['like', 'reply'],
          urgency: 'high',
        }),
      });
      await ctx.reply('Engagement requested!');
    } catch (err) {
      await ctx.reply('Failed to request engagement');
    }
  });

  return bot;
}

export function startTelegramBot(options: TelegramBotOptions) {
  const bot = createTelegramBot(options);
  bot.launch();
  return bot;
}

if (require.main === module) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const serverUrl = process.env.NETWORK_SERVER_URL;
  if (!token) {
    console.error('TELEGRAM_BOT_TOKEN required');
    process.exit(1);
  }
  startTelegramBot({ token, serverUrl });
}
