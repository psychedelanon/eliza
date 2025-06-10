export const oceanFacts = [
  "The Pacific Ocean is the largest ocean on Earth, covering more than 30% of the planet's surface.",
  'Some species of jellyfish have existed for over 500 million years, predating dinosaurs.',
  'The Mariana Trench plunges to depths of about 11,000 meters, making it the deepest known part of the oceans.',
  'Coral reefs support approximately 25% of all marine life despite covering less than 1% of the ocean floor.',
  'Water absorbs red light quickly, which is why underwater scenes often appear blue or green.',
];

export function randomOceanFact(): string {
  return oceanFacts[Math.floor(Math.random() * oceanFacts.length)];
}
