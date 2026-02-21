# ---- Build stage (installs deps) ----
FROM node:20-alpine AS build
WORKDIR /app

# Copy only package files first (better layer caching)
COPY package*.json ./
RUN npm ci --omit=dev

# Copy app source
COPY . .

# ---- Runtime stage (small image) ----
FROM node:20-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production

# Copy only what we need from build stage
COPY --from=build /app /app

# App listens on 3000 (your server.js uses 3000 by default)
EXPOSE 3000

CMD ["node", "server.js"]
