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

### Fix client procedure (failed to compile error)
Usually happens when you have more than 1 GOAT installation, can be fixed re-building the client according to the next steps.
1. Get all elements in the image
```
docker image list -> take the first characters of "IMAGE ID" from the repository "goat-client"
```
2. Delete goat-client from your image
```
docker rmi 'first characters of "IMAGE ID"' --force
```
3. Clean cache
```
docker system prune
```
after that, press "y" to continue  
  
4. Rebuild goat-client
```
docker-compose up --build --force-recreate -d client
```
Run localhost again

