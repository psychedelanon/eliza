export const goobingstonTweets = [
  "\uD83C\uDF0A Did you know? The ocean covers 71% of Earth's surface!",
  "\uD83D\uDCA7 Water is the driving force of all nature.",
  "\uD83D\uDC1F Some fish can glide through the air for over 200 meters!"
];

export interface Mention {
  id: string;
  text: string;
  username: string;
}

export const goobingstonMentions: Mention[] = [
  {
    id: '1',
    text: '@AquaAgent Love your water facts!',
    username: 'Goobingston'
  },
  {
    id: '2',
    text: '@AquaAgent Any tips to stay hydrated?',
    username: 'Goobingston'
  }
];
