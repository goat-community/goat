import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useMap } from "react-map-gl/maplibre";
import { ZodSchema } from "zod";
import { getMapExtentCQL } from "@/lib/utils/map/navigate";

export const useChartWidget = <TConfig, TQueryParams>(
  rawConfig: unknown,
  configSchema: ZodSchema<TConfig>,
  queryParamSchema: ZodSchema<TQueryParams>
) => {
  const { map } = useMap();
  const { projectId } = useParams() as { projectId: string };
  const [queryParams, setQueryParams] = useState<TQueryParams>();

  const config = useMemo(() => {
    const parsed = configSchema.safeParse(rawConfig);
    return parsed.success ? parsed.data : undefined;
  }, [rawConfig, configSchema]);

  useEffect(() => {
    if (!config || !map) return;

    const parsedParams = queryParamSchema.safeParse({
      ...(config as any).setup,
      ...(config as any).options,
    });

    if (!parsedParams.success) return;

    let newParams = parsedParams.data;
    if ((config as any).options?.filter_by_viewport) {
      newParams = { ...newParams, query: getMapExtentCQL(map) };
    }

    setQueryParams(newParams);
  }, [config, map, queryParamSchema]);

  useEffect(() => {
    if (!map || !(config as any)?.options?.filter_by_viewport) return;

    const handler = () => {
      const clqFilter = getMapExtentCQL(map);
      setQueryParams((prev) => ({ ...prev, query: clqFilter } as TQueryParams));
    };

    map.on("moveend", handler);
    return () => {
      map.off("moveend", handler);
    };
  }, [map, (config as any)?.options?.filter_by_viewport]);

  return { config, queryParams, projectId };
};

