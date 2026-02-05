# ui/Dockerfile

# ---------- Build stage ----------
FROM node:22-alpine AS builder

WORKDIR /app

# Env var for API base URL (used at build time by Next.js)
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# Install dependencies
COPY ui/package.json ui/package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy the rest of the frontend source
COPY ui/ ./

# Build Next.js app
RUN npm run build

# ---------- Runtime stage ----------
FROM node:22-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy only what we need to run the built app
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "run", "start"]
