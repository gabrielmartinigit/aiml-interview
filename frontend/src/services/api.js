import axios from "axios";

const api = axios.create({
  baseURL: "<API ENDPOINT>",
});

export default api;
