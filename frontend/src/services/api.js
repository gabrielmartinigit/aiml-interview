import axios from "axios";

const api = axios.create({
  baseURL: "https://8n0efal0r2.execute-api.us-east-1.amazonaws.com/Prod/",
});

export default api;
