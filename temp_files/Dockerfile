# Use official Node image
FROM node:18-alpine

# Set work directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
