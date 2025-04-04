# Conference CMS Frontend

This is the Angular-based frontend for the Conference Content Management System. It provides a modern, responsive interface for searching, viewing, and managing conference content with AI-powered features.

## Features

- **AI-powered content search**: Find relevant conference materials using semantic search
- **Content detail views**: View presentations, speakers, and associated materials
- **Filterable search**: Filter content by session type, date, learning level, topics, and more
- **RAG Question Answering**: Ask questions about content and get AI-generated answers
- **Responsive design**: Works on desktop, tablet, and mobile devices

## Getting Started

### Prerequisites

- Node.js 14+ and npm
- Angular CLI 13+

### Installation

1. Install dependencies:
   ```
   npm install
   ```

2. Set up environment files:

   Create or update `src/environments/environment.ts` for development:
   ```typescript
   export const environment = {
     production: false,
     apiBaseUrl: 'http://localhost:3001/api'
   };
   ```

   And `src/environments/environment.prod.ts` for production:
   ```typescript
   export const environment = {
     production: true,
     apiBaseUrl: '/api'
   };
   ```

### Development Server

Run the development server:

```
npm start
```

This command uses the proxy configuration in `proxy.conf.json` to forward API requests to the backend server. The application will be available at `http://localhost:4200/`.

### Building for Production

Build the application for production:

```
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   ├── models/          # Data models
│   │   ├── pipes/           # Custom pipes
│   │   └── directives/      # Custom directives
│   ├── assets/              # Static assets
│   └── environments/        # Environment configurations
├── angular.json             # Angular CLI configuration
├── package.json             # Dependencies and scripts
└── proxy.conf.json          # Development proxy configuration
```

## Key Components

- **Search Component**: Allows users to search for content with various filters
- **Content Detail Component**: Displays detailed view of conference content with files and presenters
- **Upload Component**: Provides interface for uploading new content
- **Header/Footer Components**: Consistent navigation and branding throughout the app

## Services

- **ContentService**: Handles API calls for content retrieval and management
- **RAGService**: Provides Retrieval-Augmented Generation capabilities
- **ConferenceDataService**: Manages conference-specific data like tracks and session types

## Development Guidelines

### Styling

The application uses Angular Material components with custom styling to maintain a consistent look and feel. Custom styles are defined in component-specific SCSS files.

### State Management

For simple state, we use Angular services with RxJS observables. For more complex state, we implement a service-based approach with behavior subjects.

### API Communication

All API calls are encapsulated in services. API responses are mapped to strongly typed models defined in the `models` directory.

## Contributing

1. Create a new branch for your feature or bug fix
2. Make your changes following the project's code style
3. Write or update tests as necessary
4. Submit a pull request with a clear description of the changes

## Deployment

The frontend can be deployed as static files to any web server. In production, it's recommended to configure the server to forward API requests to the backend service.

For deployment with the backend, build the frontend and move the output from `dist/frontend` to the backend's static files directory. 