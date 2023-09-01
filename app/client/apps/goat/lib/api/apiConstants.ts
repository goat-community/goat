// dashboard
export const ORGANIZATION_API_URL = "/api/dashboard/organization";
export const OVERVIEW_API_URL = "/api/dashboard/organizationOverview";
export const API = {
  folder: "/api/v2/content/folder",
  report: "/api/v2/content/report",
  layer: "/api/v2/content/layer",
  project: "api/v2/content/project",
};
// export const FILTERING = "http://localhost:3000/api/map/filtering/layer/";
export const FILTERING = (layer_id: string) => `http://127.0.0.1:8081/collections/${layer_id}/tiles/{z}/{x}/{y}`;