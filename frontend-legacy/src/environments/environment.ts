export const environment = {
  production: false,
  apiUrl: '/api', // Changed to relative path to use with proxy
  vertexAIApiUrl: '/api/rag', // Changed to relative path to use with proxy
  google: {
    apiKey: 'AIzaSyCAkPRgocIxXbZ2YxD65gVlmt7gXTfaaBg', // Replace with your API key from Google Cloud Console
    clientId: '652983476232-v67gfls5hujb3jb8qgvsloo016drc7go.apps.googleusercontent.com', // From client_credentials.json
    scopes: [
      'https://www.googleapis.com/auth/drive.readonly'
    ],
    redirectUri: 'http://localhost:4200/drive-callback' // Add redirect URI
  }
}; 