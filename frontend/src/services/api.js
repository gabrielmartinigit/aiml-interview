import axios from "axios";

const api = axios.create({
  baseURL: "{SimuladorApi}",
});

export default api;
