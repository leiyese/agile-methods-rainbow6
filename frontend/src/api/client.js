import axios from "axios";

const baseURL = 'http://localhost:5001';
const apiClient = axios.create({
  baseURL: `${baseURL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;