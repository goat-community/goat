import { API } from "@/lib/api/apiConstants";
import axios from "axios";

export const contentApi = {
  getFolders: () => axios.get(API.folder),
};
