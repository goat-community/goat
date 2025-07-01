import { Stack } from "@mui/material";

import { BuilderWidgetSchema } from "@/lib/validations/project";
import { dataTypes, informationTypes } from "@/lib/validations/widget";

import { useAppSelector } from "@/hooks/store/ContextHooks";

import { FilterDataConfiguration } from "@/components/builder/widgets/data/Filter";
import { NumbersDataConfiguration } from "@/components/builder/widgets/data/Numbers";
import { LayerInformationConfiguration } from "@/components/builder/widgets/information/Layers";

interface WidgetConfigurationProps {
  onChange: (widget: BuilderWidgetSchema) => void;
}

const WidgetConfiguration = ({ onChange }: WidgetConfigurationProps) => {
  const selectedBuilderItem = useAppSelector((state) => state.map.selectedBuilderItem);

  if (selectedBuilderItem?.type !== "widget" || !selectedBuilderItem?.config) {
    return null; // Don't render anything if it's not a widget or has no config
  }

  const handleConfigChange = (config: any) => {
    onChange({
      ...selectedBuilderItem,
      config,
    });
  };

  const ConfigComponent = {
    [informationTypes.Values.layers]: LayerInformationConfiguration,
    [dataTypes.Values.filter]: FilterDataConfiguration,
    [dataTypes.Values.numbers]: NumbersDataConfiguration,
  }[selectedBuilderItem.config.type as string];

  if (!ConfigComponent) {
    return null;
  }

  return (
    <Stack direction="column" spacing={2} justifyContent="space-between">
      <ConfigComponent config={selectedBuilderItem.config as never} onChange={handleConfigChange} />
    </Stack>
  );
};

export default WidgetConfiguration;
