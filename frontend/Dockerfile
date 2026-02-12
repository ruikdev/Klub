# Stage 1: Build de l'application Angular
FROM node:20-alpine AS build

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier les fichiers sources
COPY . .

# Build de l'application Angular en mode production avec SSR
RUN npm run build

# Stage 2: Image de production
FROM node:20-alpine

WORKDIR /app

# Copier les fichiers buildés depuis le stage de build
COPY --from=build /app/dist ./dist
COPY --from=build /app/package*.json ./

# Installer uniquement les dépendances de production
RUN npm ci --only=production

# Exposer le port 4200
EXPOSE 4200

# Commande pour démarrer le serveur SSR
CMD ["node", "dist/klub/server/server.mjs"]
