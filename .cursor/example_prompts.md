# Example Prompts for Cursor AI

Use these example prompts when working with Cursor AI to generate code for this project.

## Backend Development

### Creating a New API Endpoint

```
Create a new API endpoint in the backend Flask application to [describe functionality].
Follow the existing blueprint pattern in /backend/app/blueprints.
Use proper error handling and status codes.
Include type hints and docstrings.
The endpoint should be accessible at [endpoint path].
```

### Implementing a Service

```
Create a new service in backend/app/core/services to handle [functionality].
The service should include methods for [list required methods].
Follow the dependency injection pattern as seen in other services.
Include comprehensive error handling.
Add appropriate logging.
```

### Adding a Test

```
Create a pytest test file for the [component] in the backend.
Include tests for success cases, error cases, and edge cases.
Mock external dependencies where appropriate.
Follow the existing test pattern in /backend/tests.
```

## Frontend Development

### Creating a Component

```
Create a new Angular component for [describe functionality].
Place it in the appropriate directory under frontend/src/app/components.
The component should include [describe UI elements].
Implement [describe interactions] interactions.
Follow the Angular style guide and existing patterns.
```

### Creating a Service

```
Create an Angular service to handle [functionality].
Include methods for interacting with the backend API endpoints.
Implement proper error handling and observables.
Follow the existing service pattern in frontend/src/app/services.
```

### Creating a Model

```
Create a TypeScript interface/model for [describe data structure].
Include all required properties with appropriate types.
Add JSDoc comments for each property.
Place in frontend/src/app/models directory.
```

## Example Integration Scenarios

### RAG Feature Implementation

```
Implement a feature to [describe RAG functionality] using Vertex AI.
Backend: Create a service that handles the AI interaction in backend/app/core/services.
Frontend: Create a component to display and interact with the results.
Include appropriate error handling and loading states.
```

### Document Processing

```
Implement document processing for [document type].
Extract text, store in appropriate format, and generate embeddings.
Create API endpoints for uploading and processing.
Implement frontend components for the upload and display functionality.
```

## Database Queries

```
Create a database query function to [describe query purpose].
Use the existing repository pattern in backend/app/repository.
Include proper error handling and type annotations.
Add test cases covering the query functionality.
``` 