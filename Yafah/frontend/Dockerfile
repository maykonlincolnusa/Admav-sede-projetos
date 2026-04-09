# Stage 1: Build
FROM node:20-alpine AS build

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependência
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código do frontend
COPY . .

# Recebe a URL da API como argumento de build (opcional se Railway usar ENV)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Executa o build da aplicação Vite
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Copia o build final do estágio anterior para o diretório padrão do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copia a configuração personalizada do Nginx para lidar com React Router
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80
EXPOSE 80

# Comando padrão para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
