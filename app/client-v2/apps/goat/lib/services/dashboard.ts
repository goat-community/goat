import axios from "@/lib/configs/axios";
import contentData from "@/lib/utils/template_content";

export const contentDataFetcher = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(contentData);
    }, 1000); // Simulate a 1-second delay
  });
};

export const contentFoldersFetcher = async (url: string) => {
  try {
    const res = await axios.get(`${url}?pag=1&size=50`);
    return res.data;
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const contentLayersFetcher = async (url: string) => {
  try {
    const res = await axios.get(`${url}`);
    return res.data;
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const contentProjectsFetcher = async (url: string) => {
  try {
    const res = await axios.get(`${url}`);
    return res.data;
  } catch (error) {
    console.error(error);
    return null;
  }
};

export const contentReportsFetcher = async (url: string) => {
  try {
    const res = await axios.get(`${url}`);
    return res.data;
  } catch (error) {
    console.error(error);
    return null;
  }
};
