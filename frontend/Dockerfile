FROM node:22-alpine
RUN apk add --no-cache python3 curl
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npx javascript-obfuscator dist/assets --output dist/assets --config obfuscator.config.cjs
RUN chmod +x start-offline.sh
EXPOSE 8501
CMD ["sh", "start-offline.sh"]
