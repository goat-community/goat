import { Accordion, AccordionDetails, AccordionSummary, Divider, Stack, Typography } from "@mui/material";
import { type ReactNode } from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import { setActiveRightPanel } from "@/lib/store/map/slice";
import type { ProjectLayer } from "@/lib/validations/project";

import { useActiveLayer } from "@/hooks/map/LayerPanelHooks";
import { useAppDispatch } from "@/hooks/store/ContextHooks";

import { Legend } from "@/components/map/controls/Legend";
import Container from "@/components/map/panels/Container";
import ProjectLayerDropdown from "@/components/map/panels/ProjectLayerDropdown";

const AccordionHeader = ({ title }: { title: string }) => {
  return (
    <Stack spacing={2} direction="row" alignItems="center">
      <Typography variant="body2" fontWeight="bold">
        {title}
      </Typography>
    </Stack>
  );
};

const AccordionWrapper = ({ header, body }: { header: ReactNode; body: ReactNode }) => {
  return (
    <Accordion square={false}>
      <AccordionSummary
        sx={{
          my: 0,
          py: 0,
        }}
        expandIcon={<Icon iconName={ICON_NAME.CHEVRON_DOWN} style={{ fontSize: "15px" }} />}
        aria-controls="panel1a-content">
        {header}
      </AccordionSummary>
      <Divider sx={{ mt: 0, pt: 0 }} />
      <AccordionDetails sx={{ pt: 0, mt: 0 }}>{body}</AccordionDetails>
    </Accordion>
  );
};

const LayerInfo = ({ layer }: { layer: ProjectLayer }) => {
  const { t } = useTranslation("common");
  return (
    <AccordionWrapper
      header={
        <>
          <AccordionHeader title={t("layer_info")} />
        </>
      }
      body={
        <>
          <Stack spacing={2}>
            <Typography variant="body2" fontWeight="bold">
              {t("dataset_source")}
            </Typography>
            <Typography variant="body2">{layer.name}</Typography>
            <Typography variant="body2" fontWeight="bold">
              {t("type")}
            </Typography>
            <Typography variant="body2">{t(layer.type)}</Typography>
          </Stack>
        </>
      }
    />
  );
};

const Symbology = ({ layer }: { layer: ProjectLayer }) => {
  const { t } = useTranslation("common");
  return (
    <AccordionWrapper
      header={<AccordionHeader title={t("symbology")} />}
      body={<>{layer && <Legend layers={[layer]} />}</>}
    />
  );
};

const PropertiesPanel = ({ projectId }: { projectId: string }) => {
  const dispatch = useAppDispatch();
  const { t } = useTranslation("common");
  const { activeLayer } = useActiveLayer(projectId);
  return (
    <Container
      title={t("properties")}
      direction="right"
      disablePadding={true}
      close={() => dispatch(setActiveRightPanel(undefined))}
      body={
        <>
          {activeLayer && (
            <>
              <ProjectLayerDropdown projectId={projectId} />
              <LayerInfo layer={activeLayer} />
              {(activeLayer.type === "feature" || activeLayer.type === "raster") && (
                <Symbology layer={activeLayer} />
              )}
            </>
          )}
        </>
      }
    />
  );
};

export default PropertiesPanel;
