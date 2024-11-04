import { Box, Button, Divider, IconButton, Paper, Stack, Typography } from "@mui/material";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Popup } from "react-map-gl/maplibre";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import type { MapPopoverEditorProps } from "@/types/map/popover";
import { EditorModes } from "@/types/map/popover";

import useLayerFields from "@/hooks/map/CommonHooks";

import TextFieldInput from "@/components/map/panels/common/TextFieldInput";

const MapPopoverEditor: React.FC<MapPopoverEditorProps> = ({
  title,
  lngLat,
  onClose,
  onConfirm,
  layer,
  feature,
  editMode,
}) => {
  const { t } = useTranslation("common");
  const popup = useMemo(() => {
    if (editMode === EditorModes.DELETE) {
      return {
        title: t("delete_feature"),
        icon: ICON_NAME.TRASH,
        confirmText: t("delete"),
        confirmColor: "error",
      };
    } else if (editMode === EditorModes.MODIFY_ATTRIBUTES) {
      return {
        title: t("modify_attributes"),
        icon: ICON_NAME.EDIT,
        confirmText: t("save"),
        confirmColor: "primary",
      };
    } else if (editMode === EditorModes.DRAW) {
      return {
        title: t("draw_feature"),
        icon: ICON_NAME.PLUS,
        confirmText: t("save"),
        confirmColor: "primary",
      };
    }
  }, [editMode, t]);

  const { layerFields } = useLayerFields(layer?.id || "");
  const filteredLayerFields = useMemo(() => {
    return layerFields.filter((field) => field.type === "string" || field.type === "number");
  }, [layerFields]);

  const [featureProperties, setFeatureProperties] = useState<Record<string, string | number>>(
    feature?.properties || {}
  );

  return (
    <Popup onClose={onClose} longitude={lngLat[0]} latitude={lngLat[1]} closeButton={false} maxWidth="340px">
      <Box>
        <Paper elevation={0}>
          <Stack sx={{ px: 2, pt: 2 }} direction="row" alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={2} alignItems="center" sx={{ width: "100%" }}>
              {popup?.icon && <Icon iconName={popup?.icon} style={{ fontSize: 16 }} />}
              <Typography variant="body2" fontWeight="bold">
                {title || popup?.title}
              </Typography>
            </Stack>
            <IconButton onClick={onClose}>
              <Icon iconName={ICON_NAME.XCLOSE} style={{ fontSize: 16 }} />
            </IconButton>
          </Stack>
          <Divider sx={{ mb: 0 }} />
          <Box sx={{ maxHeight: "280px", overflowY: "auto", overflowX: "hidden" }}>
            {editMode === EditorModes.DELETE && (
              <Stack
                sx={{ pt: 2, px: 2 }}
                direction="row"
                spacing={2}
                alignItems="center"
                justifyContent="center">
                <Typography variant="body2" fontWeight="bold">
                  {t("delete_this_feature")}
                </Typography>
              </Stack>
            )}
            {(editMode === EditorModes.MODIFY_ATTRIBUTES || editMode === EditorModes.DRAW) && (
              <Stack sx={{ pt: 2, px: 2 }} direction="column" spacing={2} minWidth="300px">
                {filteredLayerFields.map((field) => (
                  <Stack key={field.name} direction="row" spacing={2} alignItems="center">
                    {(field.type === "string" || field.type === "number") && (
                      <TextFieldInput
                        type={field.type === "number" ? "number" : "text"}
                        label={field.name}
                        clearable={false}
                        value={featureProperties[field.name] ? featureProperties[field.name].toString() : ""}
                        onChange={(value: string) => {
                          const parsedValue = field.type === "number" ? Number(value) : value;
                          setFeatureProperties((prev) => ({ ...prev, [field.name]: parsedValue }));
                        }}
                      />
                    )}
                  </Stack>
                ))}
              </Stack>
            )}
          </Box>

          <Divider />
          <Stack
            sx={{ pb: 2, px: 2 }}
            direction="row"
            spacing={2}
            alignItems="center"
            justifyContent="flex-end">
            <Button onClick={onClose} variant="text" sx={{ borderRadius: 0 }}>
              <Typography variant="body2" fontWeight="bold">
                {t("cancel")}
              </Typography>
            </Button>
            <Button
              onClick={() => {
                onConfirm(featureProperties);
              }}
              variant="text"
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              color={(popup?.confirmColor as any) || "primary"}
              sx={{ borderRadius: 0 }}>
              <Typography variant="body2" fontWeight="bold" color="inherit">
                {popup?.confirmText}
              </Typography>
            </Button>
          </Stack>
        </Paper>
      </Box>
    </Popup>
  );
};

export default MapPopoverEditor;
