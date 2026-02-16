# Stage 1: Build de l'application Angular
FROM node:20-alpine AS build

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier les fichiers sources
COPY . .

# Build de l'application Angular en mode production
RUN npm run build

# Stage 2: Image de production avec nginx
FROM nginx:alpine

# Copier les fichiers buildés vers nginx
COPY --from=build /app/dist/klub /usr/share/nginx/html

# Copier la configuration nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposer le port 4200
EXPOSE 4200

# Démarrer nginx
CMD ["nginx", "-g", "daemon off;"]
