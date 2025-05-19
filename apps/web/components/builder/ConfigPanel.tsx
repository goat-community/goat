import { Box, Divider, Tab, Tabs, Typography } from "@mui/material";
import { styled, useTheme } from "@mui/material/styles";
import React, { useMemo, useState } from "react";

import { useTranslation } from "@/i18n/client";

import { setSelectedBuilderItem } from "@/lib/store/map/slice";
import type { BuilderPanelSchema, Project } from "@/lib/validations/project";
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

const sections = [
  {
    title: "Information",
    items: [
      { id: "layers", label: "Layers", icon: "layers" },
      { id: "bookmarks", label: "Bookmarks", icon: "bookmarks" },
      { id: "comments", label: "Comments", icon: "comments" },
    ],
  },
  {
    title: "Data",
    items: [
      { id: "filter", label: "Filter", icon: "filter" },
      { id: "table", label: "Table", icon: "table" },
      { id: "numbers", label: "Numbers", icon: "numbers" },
      { id: "featureList", label: "Feature List", icon: "featureList" },
    ],
  },
  {
    title: "Charts",
    items: [
      { id: "categories", label: "Categories", icon: "categories" },
      { id: "histogram", label: "Histogram", icon: "histogram" },
      { id: "pieChart", label: "Pie chart", icon: "pieChart" },
    ],
  },
  {
    title: "Project Elements",
    items: [
      { id: "text", label: "Text", icon: "text" },
      { id: "divider", label: "Divider", icon: "divider" },
      { id: "image", label: "Image", icon: "image" },
    ],
  },
];
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
      widget: <WidgetConfiguration />,
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
            <WidgetsTab sections={sections as never} />
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
              title="Settings"
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
