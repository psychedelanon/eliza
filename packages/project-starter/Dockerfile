# Lightweight container for AquaAgent
FROM node:18-alpine
WORKDIR /app
RUN npm install -g bun
COPY package.json .
RUN bun install --production
COPY . .
RUN bun run build
CMD ["bun", "run", "start"]
