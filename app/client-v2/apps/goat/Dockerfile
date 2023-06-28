FROM node:18-alpine AS installer
RUN corepack enable && corepack prepare pnpm@8.6.0 --activate

WORKDIR /app

COPY . .

RUN pnpm install

# Build the project
RUN pnpm turbo run build --filter=goat

FROM node:18-alpine AS runner
RUN corepack enable && corepack prepare pnpm@latest --activate

# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

WORKDIR /home/nextjs

COPY --from=installer /app/apps/goat/next.config.js .
COPY --from=installer /app/apps/goat/package.json .

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=installer --chown=nextjs:nodejs /app/apps/goat/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/goat/.next/static ./apps/goat/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/goat/public ./apps/goat/public

CMD node apps/goat/server.js
