FROM node:{node}-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:{nginx}
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
