import { Box, Divider, Tab, Tabs, Typography } from "@mui/material";
import { styled, useTheme } from "@mui/material/styles";
import React, { useMemo, useState } from "react";

import { useTranslation } from "@/i18n/client";

import { setSelectedBuilderItem } from "@/lib/store/map/slice";
import type { BuilderPanelSchema, BuilderWidgetSchema, Project } from "@/lib/validations/project";
import { builderConfigSchema } from "@/lib/validations/project";

import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import PanelConfiguration from "@/components/builder/PanelConfiguration";
import SettingsTab from "@/components/builder/SettingsTab";
import WidgetConfiguration from "@/components/builder/WidgetConfiguration";
import WidgetsTab from "@/components/builder/WidgetsTab";
import SelectedItemContainer from "@/components/map/panels/Container";
import ToolsHeader from "@/components/map/panels/common/ToolsHeader";

interface ConfigPanelProps {
  project: Project;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onProjectUpdate?: (key: string, value: any, refresh?: boolean) => void;
}

const Container = styled(Box)(({ theme }) => ({
  width: "350px",
  backgroundColor: theme.palette.background.paper,
  boxShadow: "0px 0px 10px 0px rgba(58, 53, 65, 0.1)",
}));

const TabPanel = (props: { children?: React.ReactNode; index: number; value: number }) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      style={{ height: "100%" }}
      aria-labelledby={`tab-${index}`}
      {...other}>
      {value === index && <>{children}</>}
    </div>
  );
};

const ConfigPanel: React.FC<ConfigPanelProps> = ({ project, onProjectUpdate }) => {
  const dispatch = useAppDispatch();
  const selectedBuilderItem = useAppSelector((state) => state.map.selectedBuilderItem);
  const [value, setValue] = useState(1);
  const theme = useTheme();
  const { t } = useTranslation("common");
  const builderConfig = useMemo(() => {
    const parsed = builderConfigSchema.safeParse(project?.builder_config);
    if (!parsed.success) {
      return builderConfigSchema.safeParse({ settings: {}, interface: [] }).data;
    }
    return parsed.data;
  }, [project]);
  const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const handleMapSettingsChange = async (name: string, value: boolean) => {
    if (!builderConfig) {
      return;
    }
    builderConfig.settings[name] = value;
    await onProjectUpdate?.("builder_config", builderConfig);
  };

  const handleMapSettingsReset = async () => {
    const builderConfigDefault = builderConfigSchema.safeParse({ settings: {}, interface: [] });
    if (!builderConfigDefault.success) {
      return;
    }
    await onProjectUpdate?.("builder_config", builderConfigDefault.data);
  };

  const handleMapInterfaceChange = async (builderInterface: BuilderPanelSchema[]) => {
    if (!builderConfig) {
      return;
    }
    builderConfig["interface"] = builderInterface;
    try {
      await onProjectUpdate?.("builder_config", builderConfig);
    } catch {
      dispatch(setSelectedBuilderItem(undefined));
    }
  };

  const onPanelDelete = () => {
    if (!selectedBuilderItem) {
      return;
    }
    const updatedPanels = builderConfig?.interface.filter((panel) => panel.id !== selectedBuilderItem.id);
    if (updatedPanels) handleMapInterfaceChange(updatedPanels);
  };

  const onPanelChange = (panel: BuilderPanelSchema) => {
    const updatedPanels = builderConfig?.interface.map((p) => {
      if (p.id === panel.id) {
        if (panel["element"]) {
          delete panel["element"];
        }
        return panel;
      }
      return p;
    });
    dispatch(setSelectedBuilderItem(panel));
    if (updatedPanels) handleMapInterfaceChange(updatedPanels);
  };

  const onWidgetChange = (widget: BuilderWidgetSchema) => {
    if (!selectedBuilderItem || selectedBuilderItem.type !== "widget" || !builderConfig) {
      return;
    }
    dispatch(setSelectedBuilderItem(widget));
    const updatedPanels = builderConfig?.interface.map((panel) => {
      if (panel.type === "panel") {
        const updatedWidgets = panel.widgets.map((w) => {
          if (w.id === widget.id) {
            return widget;
          }
          return w;
        });
        return {
          ...panel,
          widgets: updatedWidgets,
        };
      }
      return panel;
    });
    if (updatedPanels) {
      builderConfig["interface"] = updatedPanels;
      onProjectUpdate?.("builder_config", builderConfig, false);
    }
  };

  const renderConfiguration = () => {
    if (!selectedBuilderItem) {
      return null;
    }
    const configComponents: { [key: string]: React.ReactNode } = {
      panel: (
        <PanelConfiguration
          panel={selectedBuilderItem as BuilderPanelSchema}
          onDelete={onPanelDelete}
          onChange={onPanelChange}
        />
      ),
      widget: <WidgetConfiguration onChange={onWidgetChange} />,
    };

    return configComponents[selectedBuilderItem?.type] || null;
  };

  return (
    <Container>
      {!selectedBuilderItem && (
        <>
          <Tabs
            sx={{ minHeight: "40px" }}
            value={value}
            onChange={handleChange}
            aria-label="config panel tabs"
            variant="fullWidth">
            <Tab
              sx={{ minHeight: "40px", height: "40px" }}
              label={
                <Typography variant="body2" fontWeight="bold" sx={{ ml: 2 }} color="inherit">
                  {t("widgets")}
                </Typography>
              }
              id="tab-0"
              aria-controls="tabpanel-0"
            />
            <Tab
              sx={{ minHeight: "40px", height: "40px" }}
              label={
                <Typography variant="body2" fontWeight="bold" sx={{ ml: 2 }} color="inherit">
                  {t("settings")}
                </Typography>
              }
              id="tab-1"
              aria-controls="tabpanel-1"
            />
          </Tabs>
          <Divider sx={{ mt: 0 }} />
          <TabPanel value={value} index={0}>
            <WidgetsTab />
          </TabPanel>
          <TabPanel value={value} index={1}>
            <SettingsTab
              settings={builderConfig?.settings || {}}
              onChange={handleMapSettingsChange}
              onReset={handleMapSettingsReset}
            />
          </TabPanel>
        </>
      )}
      {selectedBuilderItem && (
        <SelectedItemContainer
          backgroundColor={theme.palette.background.paper}
          disableClose
          header={
            <ToolsHeader
              title={`${
                selectedBuilderItem?.type === "panel"
                  ? t("panel")
                  : t(selectedBuilderItem?.config?.type || "widget")
              } - ${t("settings")}`}
              onBack={() => {
                dispatch(setSelectedBuilderItem(undefined));
              }}
            />
          }
          body={renderConfiguration()}
          close={() => {}}
        />
      )}
    </Container>
  );
};

export default ConfigPanel;
