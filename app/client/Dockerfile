# develop stage
FROM node:11.1-alpine as develop-stage
WORKDIR /app
COPY package*.json ./
ARG FONTAWESOME_NPM_AUTH_TOKEN
RUN npm install
COPY . .

# build stage
FROM develop-stage as build-stage
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]