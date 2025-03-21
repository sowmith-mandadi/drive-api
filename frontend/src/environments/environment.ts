export const environment = {
  production: false,
  apiUrl: '/api', // Changed to relative path to use with proxy
  vertexAIApiUrl: '/api/rag', // Changed to relative path to use with proxy
  google: {
    apiKey: 'AIzaSyB_mMBUKeIBqn4DkcwXEpnmQeUW1DbVGfE', // Placeholder - replace with real API key
    clientId: '652983476232-v67gfls5hujb3jb8qgvsloo016drc7go.apps.googleusercontent.com', // From client_credentials.json
    scopes: [
      'https://www.googleapis.com/auth/drive.readonly'
    ]
  }
}; 