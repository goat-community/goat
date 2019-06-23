#============== Building Stage ==============
FROM node:10.15.0 as build-stage

# Change directory
WORKDIR /app

#A wildcard is used to ensure both package.json AND package-lock.json are copied
COPY package*.json ./

#install app dependencies including 'devDependencies'
RUN npm install
COPY . /app
RUN npm run build

#============= Production Stage ===============
FROM nginx:1.13.12-alpine as production-stage
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist   /usr/share/nginx/html
EXPOSE 80
CMD ["nginx","-g","daemon off;"]