import { logger } from '@elizaos/core';
import yargs from 'yargs/yargs';
import { hideBin } from 'yargs/helpers';
import colors from 'yoctocolors';
import fs from 'node:fs';
import path from 'node:path';
import { TwitterApi } from 'twitter-api-v2';

export type Action = 'like' | 'retweet' | 'reply' | 'quote' | 'follow';
export interface EngagementItem {
  account: string;
  action: Action;
  message?: string;
}
export interface EngagementArgs {
  tweet: string;
  mode: 'manual' | 'auto';
  accounts?: string;
  likes?: string;
  retweets?: string;
  replies?: string;
  quotes?: string;
  follows?: string;
  swarmSize?: number;
  dryRun?: boolean;
}

export function parseComma(list?: string): string[] {
  if (!list) return [];
  return list.split(',').map((s) => s.trim()).filter(Boolean);
}

export function parseMessageList(list?: string): Record<string, string> {
  const result: Record<string, string> = {};
  if (!list) return result;
  for (const item of list.split(',')) {
    const m = item.match(/([^:]+):"?(.*)"?/);
    if (m) result[m[1].trim()] = m[2];
  }
  return result;
}

export function tweetIdFrom(input: string): string {
  const match = input.match(/status\/(\d+)/);
  if (match) return match[1];
  return input;
}

export function twitterClientFactory(name: string): TwitterApi {
  const prefix = `TWITTER_${name.toUpperCase()}_`;
  const appKey = process.env[`${prefix}API_KEY`];
  const appSecret = process.env[`${prefix}API_SECRET`];
  const accessToken = process.env[`${prefix}ACCESS_TOKEN`];
  const accessSecret = process.env[`${prefix}ACCESS_SECRET`];
  if (!appKey || !appSecret || !accessToken || !accessSecret) {
    throw new Error(`Missing credentials for ${name}`);
  }
  return new TwitterApi({ appKey, appSecret, accessToken, accessSecret });
}

export async function generatePersonaReply(_profile: any, tweetText: string): Promise<string> {
  return `Replying to: ${tweetText.slice(0, 40)}`;
}

export async function generatePersonaQuote(_profile: any, tweetText: string): Promise<string> {
  return `Quote: ${tweetText.slice(0, 40)}`;
}

function autoSelect(args: EngagementArgs, tweetText: string): EngagementItem[] {
  const accounts = Object.keys(process.env)
    .filter((k) => k.startsWith('TWITTER_') && k.endsWith('_API_KEY'))
    .map((k) => k.replace('TWITTER_', '').replace('_API_KEY', ''));
  const unique = Array.from(new Set(accounts));
  const selected = unique.slice(0, args.swarmSize || 3);
  const actions: Action[] = ['like', 'retweet', 'reply', 'quote'];
  const weights = [0.5, 0.25, 0.15, 0.1];
  const plan: EngagementItem[] = [];
  for (const acc of selected) {
    const r = Math.random();
    let cumulative = 0;
    let action: Action = 'like';
    for (let i = 0; i < actions.length; i++) {
      cumulative += weights[i];
      if (r <= cumulative) {
        action = actions[i];
        break;
      }
    }
    let message: string | undefined;
    if (action === 'reply') message = `Auto reply from ${acc}`;
    if (action === 'quote') message = `Auto quote from ${acc}`;
    plan.push({ account: acc, action, message });
  }
  return plan;
}

export async function executePlan(items: EngagementItem[], tweetId: string, dryRun: boolean) {
  const results: any[] = [];
  for (const item of items) {
    const client = twitterClientFactory(item.account);
    try {
      if (!dryRun) {
        if (item.action === 'like') await client.v2.like(item.account, tweetId);
        if (item.action === 'retweet') await client.v2.retweet(item.account, tweetId);
        if (item.action === 'follow') await client.v2.follow(item.account, tweetId);
        if (item.action === 'reply') await client.v2.reply(item.message || '', tweetId);
        if (item.action === 'quote') await client.v2.quote(tweetId, item.message || '');
      }
      logger.success(`${item.account} ${item.action}`);
      results.push({ ...item, success: true });
    } catch (error) {
      logger.error(`${item.account} ${item.action} failed`);
      results.push({ ...item, success: false, error: (error as Error).message });
    }
  }
  const logDir = path.resolve(process.cwd(), 'logs');
  if (!fs.existsSync(logDir)) fs.mkdirSync(logDir);
  const file = path.join(logDir, `engage-${new Date().toISOString().slice(0,10).replace(/-/g,'')}.json`);
  fs.appendFileSync(file, JSON.stringify(results, null, 2) + '\n');
}

export async function engageCli(argv: string[]) {
  const args = yargs(hideBin(argv))
    .option('tweet', { type: 'string', demandOption: true })
    .option('mode', { choices: ['manual', 'auto'] as const, default: 'manual' })
    .option('accounts', { type: 'string' })
    .option('likes', { type: 'string' })
    .option('retweets', { type: 'string' })
    .option('replies', { type: 'string' })
    .option('quotes', { type: 'string' })
    .option('follows', { type: 'string' })
    .option('swarm-size', { type: 'number' })
    .option('dry-run', { type: 'boolean', default: false })
    .parseSync();

  const tweetId = tweetIdFrom(args.tweet);
  const manualLists = args.likes || args.retweets || args.replies || args.quotes || args.follows;
  const mode = manualLists ? 'manual' : args.mode;
  let plan: EngagementItem[] = [];
  if (mode === 'manual') {
    const likes = parseComma(args.likes);
    const rts = parseComma(args.retweets);
    const follows = parseComma(args.follows);
    const replies = parseMessageList(args.replies);
    const quotes = parseMessageList(args.quotes);
    for (const a of likes) plan.push({ account: a, action: 'like' });
    for (const a of rts) plan.push({ account: a, action: 'retweet' });
    for (const a of follows) plan.push({ account: a, action: 'follow' });
    for (const [a, m] of Object.entries(replies)) plan.push({ account: a, action: 'reply', message: m });
    for (const [a, m] of Object.entries(quotes)) plan.push({ account: a, action: 'quote', message: m });
  } else {
    plan = autoSelect(args as any, '');
  }

  if (args.dryRun) {
    console.log(colors.cyan('Engagement Plan:'));
    for (const item of plan) {
      const msg = `${item.account} -> ${item.action}${item.message ? ' "' + item.message + '"' : ''}`;
      console.log(colors.green(msg));
    }
    return;
  }
  await executePlan(plan, tweetId, false);
}
