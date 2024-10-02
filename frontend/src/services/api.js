import axios from "axios";

const api = axios.create({
  baseURL: "https://whk72jkapa.execute-api.us-east-1.amazonaws.com/Prod/",
});

export default api;
