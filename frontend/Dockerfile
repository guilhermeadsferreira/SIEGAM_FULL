# FROM node:18-alpine as build

# WORKDIR /app

# COPY package*.json ./
# RUN npm install

# COPY . .
# RUN npm run build -- --configuration=production

FROM nginx:alpine

# COPY --from=build /app/dist/frontend /usr/share/nginx/html
COPY /dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080