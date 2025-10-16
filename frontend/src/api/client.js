import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const apiClient = axios.create({
  baseURL: `${baseURL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;