# goat

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## Fix client procedure (failed to compile error)
Usually happens when you have more than one GOAT installation. You can fix such issues by re-building the client according to the following steps.

### 1. List images
```
docker ps -> take the first characters of the "CONTAINER_ID"
```
### 2. Stop client image
```
docker kill 'first characters of "CONTAINER_ID"'
```
### 3. Get all elements in the image
```
docker image list -> take the first characters of "IMAGE ID" from the repository "goat-client"
```
### 4. Delete goat-client from your image
```
docker rmi 'first characters of "IMAGE ID"' --force
```
### 5. Clean cache
```
docker system prune
```
after that, press "y" to continue  
  
### 6. Rebuild goat-client
```
docker-compose up --build --force-recreate -d client
```
Go to http://localhost again.

