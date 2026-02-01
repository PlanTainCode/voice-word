FROM node:20-alpine AS builder

WORKDIR /app

# Установка bun
RUN npm install -g bun

# Копируем package.json
COPY package.json bun.lockb* ./

# Устанавливаем зависимости
RUN bun install

# Копируем исходники
COPY . .

# Билд
ARG NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}
RUN bun run build

# Production образ
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/.output /app/.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
