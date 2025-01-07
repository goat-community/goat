import { createSelector } from "@reduxjs/toolkit";
import type { RootState } from "@/lib/store";
import { SYSTEM_LAYERS_IDS } from "@/lib/constants";

export const selectProjectLayers = (state: RootState) => state.layers.projectLayers;
export const selectProject = (state: RootState) => state.map.project;

export const selectFilteredProjectLayers = createSelector(
  [
    selectProjectLayers,
    selectProject,
    (_: RootState, excludeLayerTypes: string[] = []) => excludeLayerTypes,
    (_: RootState, excludeLayerIds: string[] = [...SYSTEM_LAYERS_IDS]) => excludeLayerIds,
  ],
  (projectLayers, project, excludeLayerTypes, excludeLayerIds) => {
    if (!projectLayers || !project) return [];
    if (!project.layer_order) return projectLayers;

    const filteredLayers = projectLayers.filter(
      (layer) => !excludeLayerTypes.includes(layer.type) && !excludeLayerIds.includes(layer.layer_id)
    );

    return filteredLayers.sort(
      (a, b) => project.layer_order.indexOf(a.id) - project.layer_order.indexOf(b.id)
    );
  }
);
