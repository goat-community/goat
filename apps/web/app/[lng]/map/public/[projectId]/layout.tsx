import { SEO_BASE_URL } from "@/lib/constants";
import { getLocalizedMetadata } from "@/lib/metadata";

import MapPage from "@/app/[lng]/map/public/[projectId]/page";

export const PROJECTS_API_BASE_URL = new URL("api/v2/project", process.env.NEXT_PUBLIC_API_URL).href;

export async function generateMetadata({ params: { projectId, lng } }) {
  const publicProject = await fetch(`${PROJECTS_API_BASE_URL}/${projectId}/public`).then((res) => res.json());
  if (publicProject?.config?.project?.name && lng) {
    const title = `${publicProject.config.project.name} | GOAT`;
    const url = `${SEO_BASE_URL}/${lng}/map/public/${projectId}`;
    return getLocalizedMetadata(
      lng,
      {
        en: {
          title,
        },
        de: {
          title,
        },
      },
      {
        openGraphUrl: url,
        robotsIndex: true,
      }
    );
  }
  return {};
}

export default function PageLayout({ params: { projectId } }) {
  return <MapPage params={{ projectId }} />;
}
