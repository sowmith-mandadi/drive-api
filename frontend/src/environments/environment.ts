export const environment = {
  production: false,
  apiUrl: '/api', // Changed to relative path to use with proxy
  vertexAIApiUrl: '/api/rag', // Changed to relative path to use with proxy
  google: {
    apiKey: 'AIzaSyB_mMBUKeIBqn4DkcwXEpnmQeUW1DbVGfE', // Placeholder - replace with real API key
    clientId: '912741596522-o66d95l1m46feg4p4v1c4elscq6iv6dq.apps.googleusercontent.com', // Placeholder - replace with real client ID
    scopes: [
      'https://www.googleapis.com/auth/drive.readonly'
    ]
  }
}; 