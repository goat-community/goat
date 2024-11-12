import { LoadingButton } from "@mui/lab";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { toast } from "react-toastify";

import { useTranslation } from "@/i18n/client";

import { useJobs } from "@/lib/api/jobs";
import { layerFeatureUrlUpload, layerFileUpload, updateLayerDataset } from "@/lib/api/layers";
import { setRunningJobIds } from "@/lib/store/jobs/slice";
import { externalDatasetFeatureUrlSchema } from "@/lib/validations/layer";

import type { ContentDialogBaseProps } from "@/types/dashboard/content";

import { useFileUpload } from "@/hooks/dashboard/ContentHooks";
import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";

import { MuiFileInput } from "@/components/common/FileInput";

const DatasetUpdateModal: React.FC<ContentDialogBaseProps> = ({ open, onClose, content }) => {
  const { t } = useTranslation("common");
  const [isBusy, setIsBusy] = useState(false);
  const { fileValue, setFileValue, fileUploadError, setFileUploadError, handleChange, acceptedFileTypes } =
    useFileUpload();
  const dispatch = useAppDispatch();
  const { mutate } = useJobs({
    read: false,
  });
  const runningJobIds = useAppSelector((state) => state.jobs.runningJobIds);
  const handleOnClose = () => {
    setIsBusy(false);
    setFileValue(undefined);
    setFileUploadError(undefined);
    onClose?.();
  };
  const handleUpdate = async () => {
    try {
      setIsBusy(true);
      let uploadResponse;
      if (content?.data_type === "wfs") {
        const featureUrlPayload = externalDatasetFeatureUrlSchema.parse({
          data_type: "wfs",
          url: content.other_properties.url,
          other_properties: content.other_properties,
        });
        uploadResponse = await layerFeatureUrlUpload(featureUrlPayload);
      } else if (fileValue) {
        uploadResponse = await layerFileUpload(fileValue);
      }
      if (!uploadResponse) {
        throw new Error("Failed to upload dataset");
      }
      const datasetId = uploadResponse.dataset_id;
      const layerId = content.id;
      const response = await updateLayerDataset(layerId, datasetId);
      const jobId = response?.job_id;
      if (jobId) {
        mutate();
        dispatch(setRunningJobIds([...runningJobIds, jobId]));
      }
      toast.info(`"${t("dataset_update")}" - ${t("job_started")}`);
    } catch (error) {
      toast.error(t("error_update_dataset"));
    } finally {
      setIsBusy(false);
      onClose && onClose();
    }
  };
  return (
    <>
      <Dialog open={open} onClose={handleOnClose} fullWidth maxWidth="sm">
        <DialogTitle>{`${t("dataset_update")} - "${content.name}"`}</DialogTitle>
        <DialogContent>
          <Box sx={{ width: "100%" }}>
            {content.data_type === "wfs" && (
              <Stack direction="column" spacing={4}>
                <Typography variant="body2">
                  <b>{t("url")}:</b> {content.other_properties?.url}
                </Typography>
                <Typography variant="body2">
                  <b>{t("layer")}:</b> {content.other_properties?.layers}
                </Typography>
              </Stack>
            )}
            {!content.data_type && (
              <>
                <Typography variant="caption">{t("select_file_to_upload")}</Typography>
                <MuiFileInput
                  sx={{
                    my: 2,
                  }}
                  inputProps={{
                    accept: acceptedFileTypes.join(","),
                  }}
                  fullWidth
                  error={!!fileUploadError}
                  helperText={fileUploadError}
                  value={fileValue}
                  multiple={false}
                  onChange={handleChange}
                  placeholder={`${t("eg")} file.gpkg, file.geojson, shapefile.zip`}
                />
                <Typography variant="caption">
                  {t("supported")} <b>GeoPackage</b>, <b>GeoJSON</b>, <b>Shapefile (.zip)</b>, <b>KML</b>,{" "}
                  <b>CSV</b>, <b>XLSX</b>
                </Typography>
              </>
            )}
          </Box>
        </DialogContent>

        <DialogActions
          disableSpacing
          sx={{
            pt: 6,
            pb: 2,
          }}>
          <Stack direction="row" spacing={2}>
            <Button onClick={handleOnClose} variant="text">
              <Typography variant="body2" fontWeight="bold">
                {t("cancel")}
              </Typography>
            </Button>

            <LoadingButton
              disabled={isBusy || (!fileValue && content.data_type !== "wfs")}
              onClick={handleUpdate}
              variant="outlined"
              color="primary"
              loading={isBusy}>
              <Typography variant="body2" fontWeight="bold" color="inherit">
                {t("update")}
              </Typography>
            </LoadingButton>
          </Stack>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DatasetUpdateModal;
