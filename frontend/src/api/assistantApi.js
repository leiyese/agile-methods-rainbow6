import apiClient from './client.js';

export const askAssistant = async (question) => {
  try {
    const response = await apiClient.post('/answer', {
      question: question
    });
    
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('API Error:', error);
    
    return {
      success: false,
      error: error.response?.data?.message || 'Something went wrong',
      status: error.response?.status
    };
  }
};
