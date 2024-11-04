import useSWR from "swr";

import { fetchWithAuth, fetcher } from "@/lib/api/fetcher";
import type { GetContentQueryParams } from "@/lib/validations/common";
import type {
  PostProject,
  Project,
  ProjectLayer,
  ProjectPaginated,
  ProjectViewState,
} from "@/lib/validations/project";
import type {
  PostScenario,
  ScenarioFeaturePost,
  ScenarioFeatures,
  ScenarioFeatureUpdate,
  ScenarioResponse,
} from "@/lib/validations/scenario";

export const PROJECTS_API_BASE_URL = new URL("api/v2/project", process.env.NEXT_PUBLIC_API_URL).href;

export const useProjects = (queryParams?: GetContentQueryParams) => {
  const { data, isLoading, error, mutate, isValidating } = useSWR<ProjectPaginated>(
    [`${PROJECTS_API_BASE_URL}`, queryParams],
    fetcher
  );
  return {
    projects: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const useProject = (projectId?: string) => {

  const { data, isLoading, error, mutate, isValidating } = useSWR<Project>(
    () => (projectId ? [`${PROJECTS_API_BASE_URL}/${projectId}`] : null),
    fetcher
  );

  return {
    project: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const useProjectLayers = (projectId?: string) => {

  const { data, isLoading, error, mutate, isValidating } = useSWR<ProjectLayer[]>(
    () => (projectId ? [`${PROJECTS_API_BASE_URL}/${projectId}/layer`] : null),
    fetcher
  );

  return {
    layers: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const useProjectScenarios = (projectId: string) => {
  const { data, isLoading, error, mutate, isValidating } = useSWR<ScenarioResponse>(
    [`${PROJECTS_API_BASE_URL}/${projectId}/scenario`],
    fetcher
  );
  return {
    scenarios: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const useProjectScenarioFeatures = (projectId: string, scenarioId?: string | null) => {
  const { data, isLoading, error, mutate, isValidating } = useSWR<ScenarioFeatures>(
    () => (scenarioId ? [`${PROJECTS_API_BASE_URL}/${projectId}/scenario/${scenarioId}/features`] : null),
    fetcher
  );
  return {
    scenarioFeatures: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const useProjectInitialViewState = (projectId: string) => {
  const { data, isLoading, error, mutate, isValidating } = useSWR<ProjectViewState>(
    [`${PROJECTS_API_BASE_URL}/${projectId}/initial-view-state`],
    fetcher
  );
  return {
    initialView: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const useProjectLayerChartData = (projectId: string, layerId: number, cumSum: boolean = false) => {
  const { data, isLoading, error, mutate, isValidating } = useSWR(
    [`${PROJECTS_API_BASE_URL}/${projectId}/layer/${layerId}/chart-data?cumsum=${cumSum}`],
    fetcher
  );
  return {
    chartData: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};

export const updateProjectInitialViewState = async (projectId: string, payload: ProjectViewState) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/initial-view-state`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to update project initial view state");
  }
  return await response.json();
};

export const updateProjectLayer = async (projectId: string, layerId: number, payload: ProjectLayer) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/layer/${layerId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw Error(`Failed to update project layer ${layerId}`);
  }
  return await response.json();
};

export const deleteProjectLayer = async (projectId: string, layerId: number) => {
  try {
    await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/layer?layer_project_id=${layerId}`, {
      method: "DELETE",
    });
  } catch (error) {
    console.error(error);
    throw Error(`deleteProjectLayer: unable to delete layer with id ${layerId}`);
  }
};

export const addProjectLayers = async (projectId: string, layerIds: string[]) => {
  //todo: fix the api for this. This structure doesn't make sense.
  //layer_ids=1&layer_ids=2&layer_ids=3
  const layerIdsParams = layerIds.map((layerId) => {
    return `layer_ids=${layerId}`;
  });

  const response = await fetchWithAuth(
    `${PROJECTS_API_BASE_URL}/${projectId}/layer?${layerIdsParams.join("&")}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  if (!response.ok) {
    throw new Error("Failed to add layers to project");
  }
  return await response.json();
};

export const updateProject = async (projectId: string, payload: PostProject) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to update project");
  }
  return await response.json();
};

export const createProject = async (payload: PostProject): Promise<Project> => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create project");
  }
  return await response.json();
};

export const deleteProject = async (id: string) => {
  try {
    await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${id}`, {
      method: "DELETE",
    });
  } catch (error) {
    console.error(error);
    throw Error(`deleteProject: unable to delete project with id ${id}`);
  }
};

export const createProjectScenario = async (projectId: string, payload: PostScenario) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/scenario`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create project scenario");
  }
  return await response.json();
};

export const updateProjectScenario = async (projectId: string, scenarioId: string, payload: PostScenario) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/scenario/${scenarioId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to update project scenario");
  }
  return await response.json();
};

export const deleteProjectScenario = async (projectId: string, scenarioId: string) => {
  try {
    await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/scenario/${scenarioId}`, {
      method: "DELETE",
    });
  } catch (error) {
    console.error(error);
    throw Error(`deleteProjectScenario: unable to delete scenario with id ${scenarioId}`);
  }
};

export const deleteProjectScenarioFeature = async (
  projectId: string,
  project_layer_id: number,
  scenarioId: string,
  featureId: string | number,
  h33?: number
) => {
  let url = `${PROJECTS_API_BASE_URL}/${projectId}/layer/${project_layer_id}/scenario/${scenarioId}/features/${featureId}`;

  // H33 is mandatory for user data. It can be undefined for new features only.
  if (h33 !== undefined) {
    url += `?h3_3=${h33}`;
  }

  const response = await fetchWithAuth(url, {
    method: "DELETE",
  });

  if (!response.ok) throw await response.json();
  return response;
};

export const updateProjectScenarioFeatures = async (
  projectId: string,
  project_layer_id: number,
  scenarioId: string,
  payload: ScenarioFeatureUpdate[]
) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/layer/${project_layer_id}/scenario/${scenarioId}/features`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to update project scenario features");
  }
  return await response.json();
}

export const createProjectScenarioFeatures = async (
  projectId: string,
  project_layer_id: number,
  scenarioId: string,
  payload: ScenarioFeaturePost[]
) => {
  const response = await fetchWithAuth(`${PROJECTS_API_BASE_URL}/${projectId}/layer/${project_layer_id}/scenario/${scenarioId}/features`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create project scenario features");
  }
  return await response.json();
}
