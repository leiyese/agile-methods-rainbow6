# RAG Knowledge Assistant Frontend

This is the frontend for the RAG Knowledge Assistant application, built with React.

## Features

- Search documents using natural language queries
- Upload and process documents (PDF, DOCX, TXT)
- Analyze and compare multiple documents
- View document similarities, differences, and conflicts

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:5000/api
```

3. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000.

## Available Scripts

- `npm start` - Starts the development server
- `npm test` - Runs tests
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App

## Project Structure

```
frontend/
├── public/             # Static files
├── src/
│   ├── components/     # React components
│   ├── services/       # API services
│   ├── App.js          # Main application component
│   └── index.js        # Entry point
└── package.json        # Dependencies and scripts
```

## Learn More

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).
