export const environment = {
  production: true,
  apiUrl: '/api', // Use relative URL in production
  vertexAIApiUrl: '/api/rag', // Use relative URL in production
  google: {
    apiKey: 'AIzaSyB_mMBUKeIBqn4DkcwXEpnmQeUW1DbVGfE', // Replace with real API key
    clientId: '912741596522-o66d95l1m46feg4p4v1c4elscq6iv6dq.apps.googleusercontent.com', // Replace with real client ID
    scopes: [
      'https://www.googleapis.com/auth/drive.readonly'
    ]
  }
}; 