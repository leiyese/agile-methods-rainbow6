import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});
    
export default apiClient;