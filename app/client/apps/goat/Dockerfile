FROM node:18-alpine AS base

FROM base AS builder
RUN apk add --no-cache libc6-compat
RUN apk update
# Set working directory
WORKDIR /app
RUN npm install -g turbo
COPY . .
COPY .env.docker /app/apps/goat/.env
RUN turbo prune --scope=@p4b/goat --docker

# Add lockfile and package.json's of isolated subworkspace
FROM base AS installer
RUN apk add --no-cache libc6-compat
RUN apk update
WORKDIR /app

# First install the dependencies (as they change less often)
COPY --from=builder /app/out/json/ .
COPY --from=builder /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
RUN corepack enable
RUN pnpm install --frozen-lockfile

# Build the project
COPY --from=builder /app/out/full/ .
RUN pnpm dlx turbo run build --filter=goat

FROM base AS runner
WORKDIR /app

# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

COPY --from=installer /app/apps/goat/next.config.js .
COPY --from=installer /app/apps/goat/package.json .

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=installer --chown=nextjs:nodejs /app/apps/goat/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/goat/.next/static ./apps/goat/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/goat/public ./apps/goat/public

ENV HOSTNAME localhost

CMD node apps/goat/server.js
