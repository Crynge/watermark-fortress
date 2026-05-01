FROM node:22-alpine

WORKDIR /app
COPY apps/web/package.json /app/package.json
COPY apps/web/tsconfig.json /app/tsconfig.json
COPY apps/web/tsconfig.app.json /app/tsconfig.app.json
COPY apps/web/tsconfig.node.json /app/tsconfig.node.json
COPY apps/web/vite.config.ts /app/vite.config.ts
COPY apps/web/eslint.config.js /app/eslint.config.js
COPY apps/web/index.html /app/index.html
COPY apps/web/public /app/public
COPY apps/web/src /app/src
RUN npm install
RUN npm run build

EXPOSE 4174
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4174"]
