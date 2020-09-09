FROM node:13.7.0-alpine3.10
ARG REACT_APP_BACKEND_HOST

# Pre install node dependencies
WORKDIR /home/node/app
COPY ./src/package.json ./
RUN yarn install

# Copy and run the app
COPY ./src/ ./
CMD yarn run start
