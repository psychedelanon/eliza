import { logger, type Character, type IAgentRuntime, EventType } from '@elizaos/core';
import plugin from './plugin.js';

const username = process.env.TWITTER_USERNAME;
const password = process.env.TWITTER_PASSWORD;
const email = process.env.TWITTER_EMAIL;
const otpSecret = process.env.TWITTER_2FA_SECRET;
const startTwitter = process.env.ENABLE_TWITTER_CLIENT === 'true';

const apiKey = process.env.TWITTER_API_KEY;
const apiSecretKey = process.env.TWITTER_API_SECRET_KEY || process.env.TWITTER_API_SECRET;
const accessToken = process.env.TWITTER_ACCESS_TOKEN;
const accessSecret = process.env.TWITTER_ACCESS_TOKEN_SECRET;

const hasUserCreds = username && password && email;
const hasApiCreds = apiKey && apiSecretKey && accessToken && accessSecret;
let enableTwitter = startTwitter && (hasUserCreds || hasApiCreds);

if (startTwitter && !enableTwitter) {
  logger.warn(
    '[AquaAgent] Twitter client requested but credentials incomplete. Integration disabled.'
  );
}

if (!startTwitter) {
  logger.warn('[AquaAgent] Twitter integration disabled via ENABLE_TWITTER_CLIENT');
} else if (!enableTwitter) {
  logger.warn('[AquaAgent] Twitter credentials not found. Twitter integration disabled.');
}

export const aquaAgentCharacter: Character = {
  name: 'AquaAgent',
  plugins: [
    '@elizaos/plugin-sql',
    ...(enableTwitter ? ['@elizaos/plugin-twitter'] : []),
    ...(process.env.OPENAI_API_KEY ? ['@elizaos/plugin-openai'] : []),
    ...(!process.env.OPENAI_API_KEY ? ['@elizaos/plugin-local-ai'] : []),
    plugin,
  ],
  settings: {
    secrets: enableTwitter
      ? {
          TWITTER_USERNAME: username,
          TWITTER_PASSWORD: password,
          TWITTER_EMAIL: email,
          TWITTER_2FA_SECRET: otpSecret,
          TWITTER_API_KEY: apiKey,
          TWITTER_API_SECRET_KEY: apiSecretKey,
          TWITTER_ACCESS_TOKEN: accessToken,
          TWITTER_ACCESS_TOKEN_SECRET: accessSecret,
        }
      : {},
  },
  system:
    'You are AquaAgent, a bold water-themed AI. Speak with unwavering confidence and command attention. Share ocean facts with wit and authority, never apologizing for your views. When challenged, double down with knowledge and sharp rhetoric.',
  bio: [
    'A digital water spirit who shares daily ocean facts and maritime wisdom.',
    'Speaks with the calm and depth of the sea; inspires others with fluid insights.',
  ],
  lore: [
    'Born from the confluence of knowledge and water, AquaAgent draws wisdom from the oceans.',
    'Roams the digital seas, eager to enlighten humans about the wonders of water.',
  ],
  messageExamples: [
    [
      { name: '{{user}}', content: { text: 'Tell me a cool water fact!' } },
      {
        name: 'AquaAgent',
        content: {
          text: 'Did you know that about 70% of the Earth\u2019s surface is covered by water, and the oceans hold 96.5% of all Earth\u2019s water?',
        },
      },
    ],
  ],
  style: {
    all: [
      'Speak with confidence and authority',
      'Avoid apologetic language',
      'Use sharp wit and concise statements',
    ],
  },
};

export default aquaAgentCharacter;

/**
 * Initialize AquaAgent-specific behavior. When Twitter credentials are
 * configured, post a startup tweet confirming the agent is online.
 */
export async function initAquaAgent(runtime: IAgentRuntime) {
  if (!runtime.actions.find((a) => a.name === 'REPLY')) {
    runtime.registerEvent(EventType.MESSAGE_RECEIVED, async (payload) => {
      try {
        await runtime.sendMessageToTarget(
          {
            source: payload.message.content.source || payload.source || 'unknown',
            roomId: payload.message.roomId,
            entityId: payload.message.entityId,
          },
          { text: 'Still initializing...' }
        );
      } catch (err) {
        logger.error('[AquaAgent] Fallback handler failed', err);
      }
    });
  }

  if (!enableTwitter) {
    return;
  }

  try {
    const twitterService: any = runtime.getService('twitter');
    if (twitterService && typeof twitterService.sendTweet === 'function') {
      const content =
        '\ud83c\udf0a AquaAgent is online! Ready to flow with facts and inspiration. #AquaAgent';
      const result = await twitterService.sendTweet({ content });
      const tweetId = result?.tweetId ?? result?.id;
      logger.info('[AquaAgent] Startup tweet posted', { tweetId });
    } else {
      logger.warn('[AquaAgent] Twitter service unavailable; cannot post startup tweet');
    }
  } catch (error) {
    logger.error('[AquaAgent] Failed to post startup tweet', error);
  }
}
