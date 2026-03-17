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

# Stage 2: Runtime Node sans nginx
FROM node:20-alpine AS runtime

WORKDIR /app

# Serveur statique léger pour exposer la build
RUN npm install -g serve

# Copier la build Angular
COPY --from=build /app/dist/klub ./dist/klub

# Exposer le port HTTP
EXPOSE 80

# Démarrer le serveur statique
CMD ["serve", "-s", "dist/klub", "-l", "80"]
