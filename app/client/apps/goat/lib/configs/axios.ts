import axios from "axios";

// Create a new instance of Axios with your desired defaults
const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Credentials": "true",
    Accept: "application/json",
  },
});

export default instance;
