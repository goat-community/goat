import projectDataExample from "@/lib/utils/template_project";
import type { Project } from "@/types/map/project";

export async function fetchProject(): Promise<Project> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(projectDataExample);
    }, 1000); // Simulate a 1-second delay
  });
}
