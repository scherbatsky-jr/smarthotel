FROM node:20-slim

WORKDIR /app

# Only copy lockfile + package.json
COPY package.json yarn.lock ./

# Install deps on correct platform
RUN yarn install

# Copy rest of the app
COPY . .

EXPOSE 5173
CMD ["yarn", "dev", "--host"]