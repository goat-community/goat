import { Stack } from "@mui/material";
import { useMemo } from "react";

import { hasNestedSchemaPath } from "@/lib/utils/zod";
import type { BuilderWidgetSchema } from "@/lib/validations/project";
import { widgetSchemaMap } from "@/lib/validations/widget";

import { useAppSelector } from "@/hooks/store/ContextHooks";

import {
  WidgetData,
  WidgetInfo,
  WidgetOptions,
} from "@/components/builder/widgets/common/WidgetCommonConfigs";

interface WidgetConfigurationProps {
  onChange: (widget: BuilderWidgetSchema) => void;
}

const WidgetConfiguration = ({ onChange }: WidgetConfigurationProps) => {
  const selectedBuilderItem = useAppSelector((state) => state.map.selectedBuilderItem);
  if (selectedBuilderItem?.type !== "widget" || !selectedBuilderItem?.config) {
    return null; // Don't render anything if it's not a widget or has no config
  }

  const schema = widgetSchemaMap[selectedBuilderItem?.config?.type];
  if (!schema) {
    console.error(`Widget schema not found for type: ${selectedBuilderItem?.config?.type}`);
    return null;
  }

  const handleConfigChange = (config: never) => {
    onChange({
      ...selectedBuilderItem,
      config,
    });
  };

  const hasDataConfig = useMemo(() => {
    return hasNestedSchemaPath(schema, "setup.layer_project_id");
  }, [schema]);

  return (
    <Stack direction="column" spacing={2} justifyContent="space-between">
      <WidgetInfo config={selectedBuilderItem.config} onChange={handleConfigChange} />
      {hasDataConfig && <WidgetData config={selectedBuilderItem.config} onChange={handleConfigChange} />}
      <WidgetOptions config={selectedBuilderItem.config} onChange={handleConfigChange} />
    </Stack>
  );
};

export default WidgetConfiguration;
