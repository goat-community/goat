import { useParams } from "next/navigation";
import { useMemo } from "react";

import { useTranslation } from "@/i18n/client";

import { type StatisticOperation, statisticOperationEnum } from "@/lib/validations/common";

import type { SelectorItem } from "@/types/map/common";

import useLayerFields from "@/hooks/map/CommonHooks";
import { useLayerDatasetId, useStatisticValues } from "@/hooks/map/ToolsHooks";

import LayerFieldSelector from "@/components/map/common/LayerFieldSelector";
import Selector from "@/components/map/panels/common/Selector";
import TextFieldInput from "@/components/map/panels/common/TextFieldInput";

export type StatisticConfig = {
  method?: StatisticOperation | undefined;
  value?: string | undefined;
};

export const StatisticSelector = ({
  layerProjectId,
  value,
  onChange,
}: {
  layerProjectId: number;
  value?: StatisticConfig;
  onChange?: (value: StatisticConfig) => void;
}) => {
  const { t } = useTranslation("common");
  const { projectId } = useParams();

  const { statisticMethods } = useStatisticValues(true);
  const layerDatasetId = useLayerDatasetId(layerProjectId, projectId as string);
  const selectedStatisticMethod = useMemo(() => {
    return statisticMethods.find((method) => method.value === value?.method);
  }, [statisticMethods, value?.method]);

  const isStatisticFieldVisible = useMemo(() => {
    return (
      selectedStatisticMethod?.value !== statisticOperationEnum.Enum.count &&
      selectedStatisticMethod?.value !== statisticOperationEnum.Enum.expression
    );
  }, [selectedStatisticMethod]);

  const { layerFields: statisticLayerFields } = useLayerFields(
    layerDatasetId || "",
    isStatisticFieldVisible ? "number" : undefined
  );

  const selectedField = useMemo(() => {
    return statisticLayerFields.find((field) => field.name === value?.value);
  }, [statisticLayerFields, value?.value]);

  return (
    <>
      {layerProjectId && (
        <Selector
          selectedItems={selectedStatisticMethod}
          setSelectedItems={(item: SelectorItem[] | SelectorItem | undefined) => {
            if (onChange) {
              onChange({
                method: (item as SelectorItem)?.value as StatisticOperation | undefined,
                value: undefined,
              });
            }
          }}
          items={statisticMethods}
          label={t("select_statistic_method")}
          placeholder={t("select_statistic_method_placeholder")}
          tooltip={t("select_statistic_method_tooltip")}
        />
      )}

      {selectedStatisticMethod && layerDatasetId && isStatisticFieldVisible && (
        <LayerFieldSelector
          fields={statisticLayerFields}
          selectedField={selectedField}
          setSelectedField={(field) => {
            if (onChange) {
              onChange({
                method: selectedStatisticMethod?.value as StatisticOperation | undefined,
                value: field?.name,
              });
            }
          }}
          label={t("select_field_to_calculate_statistics")}
          tooltip={t("select_field_to_calculate_statistics_tooltip")}
        />
      )}
      {selectedStatisticMethod?.value === statisticOperationEnum.Enum.expression && (
        <TextFieldInput
          type="text"
          label={t("expression")}
          placeholder={t("enter_expression_placeholder")}
          clearable={false}
          value={value?.value || ""}
          onChange={(expression: string) => {
            if (onChange) {
              onChange({
                method: statisticOperationEnum.Enum.expression,
                value: expression,
              });
            }
          }}
        />
      )}
    </>
  );
};
