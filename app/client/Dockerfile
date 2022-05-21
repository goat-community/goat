# develop stage
FROM node:11.1-alpine as develop-stage
WORKDIR /app

ARG VUE_APP_I18N_LOCALE=en
ARG VUE_APP_I18N_FALLBACK_LOCALE=en
ARG VUE_APP_SEARCH_KEY=ca068d7840bca4
ARG VUE_APP_SEARCH_URL=https://api.locationiq.com/v1
ARG FONTAWESOME_NPM_AUTH_TOKEN

COPY . .
RUN if [[ -n "$FONTAWESOME_NPM_AUTH_TOKEN" ]] ; then \
  npm config set "@fortawesome:registry" https://npm.fontawesome.com/ && \
  npm config set "//npm.fontawesome.com/:_authToken" $FONTAWESOME_NPM_AUTH_TOKEN && \
  echo "//registry.npmjs.org/:_authToken=${FONTAWESOME_NPM_AUTH_TOKEN}" > /app/.npmrc  && \
  npm install --save @fortawesome/fontawesome-pro ; \
  else rm -f /app/.npmrc ; fi

ENV VUE_APP_I18N_LOCALE=$VUE_APP_I18N_LOCALE
ENV VUE_APP_I18N_FALLBACK_LOCALE=$VUE_APP_I18N_FALLBACK_LOCALE
ENV VUE_APP_SEARCH_KEY=$VUE_APP_SEARCH_KEY
ENV VUE_APP_SEARCH_URL=$VUE_APP_SEARCH_URL
ENV VUE_APP_FONTAWESOME_NPM_AUTH_TOKEN=$FONTAWESOME_NPM_AUTH_TOKEN
RUN npm install && \
  rm -f /app/.npmrc

# build stage

FROM develop-stage as build-stage
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]