FROM node:20-alpine

WORKDIR /app

RUN corepack enable

# Copy yarn installation files first for cache optimization
COPY ./src/package.json ./src/yarn.lock ./src/.pnp* ./src/.yarnrc.yml ./
COPY ./src/.yarn ./.yarn

RUN yarn install --immutable

COPY ./src ./

EXPOSE 3000

CMD ["yarn", "start", "--host"]
