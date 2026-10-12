import CloseIcon from "@mui/icons-material/Close";
import { Box, CircularProgress, IconButton, Stack, Typography } from "@mui/material";
import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { uploadAsset } from "@/lib/api/assets";
import { ASSETS_MAX_FILE_SIZE_MB, assetTypeEnum } from "@/lib/validations/assets";

interface SocialPreviewImagePickerProps {
  label: string;
  imageUrl?: string;
  defaultImageUrl?: string;
  helperText?: string;
  onChange: (url: string | undefined) => void;
}

const ASPECT_RATIO = 1200 / 630;

export const SocialPreviewImagePicker: React.FC<SocialPreviewImagePickerProps> = ({
  label,
  imageUrl,
  defaultImageUrl,
  helperText,
  onChange,
}) => {
  const { t } = useTranslation("common");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const displayedUrl = imageUrl || defaultImageUrl;

  const handleFile = async (file: File) => {
    const maxSize = ASSETS_MAX_FILE_SIZE_MB * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error(`${t("maximum_image_size_is")} ${ASSETS_MAX_FILE_SIZE_MB}MB`);
      return;
    }
    if (!file.type.startsWith("image/")) {
      toast.error(t("image_upload_failed"));
      return;
    }

    setIsUploading(true);
    try {
      const asset = await uploadAsset(file, assetTypeEnum.Enum.image, {
        displayName: file.name,
        category: "social_preview",
      });
      onChange(asset.url);
    } catch {
      toast.error(t("image_upload_failed"));
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  return (
    <Box>
      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: "block" }}>
        {label}
      </Typography>
      <input type="file" accept="image/*" hidden ref={fileInputRef} onChange={handleFileChange} />
      <Box
        onClick={() => !isUploading && fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          if (!isDragging) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        sx={{
          position: "relative",
          width: "100%",
          aspectRatio: `${ASPECT_RATIO}`,
          border: "1px dashed",
          borderColor: isDragging ? "primary.main" : "divider",
          borderRadius: 1,
          backgroundColor: isDragging ? "action.hover" : "transparent",
          cursor: isUploading ? "wait" : "pointer",
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "border-color 0.15s, background-color 0.15s",
          "&:hover": { borderColor: "primary.main" },
        }}>
        {displayedUrl && (
          <Box
            component="img"
            src={displayedUrl}
            alt={t("social_preview")}
            sx={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        )}
        {!displayedUrl && (
          <Stack alignItems="center" spacing={0.5} sx={{ pointerEvents: "none" }}>
            <Icon iconName={ICON_NAME.IMAGE} />
            <Typography variant="caption" color="text.secondary">
              {t("upload_or_drop_image")}
            </Typography>
          </Stack>
        )}
        {isUploading && (
          <Box
            sx={{
              position: "absolute",
              inset: 0,
              backgroundColor: "rgba(0,0,0,0.4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}>
            <CircularProgress size={28} sx={{ color: "white" }} />
          </Box>
        )}
        {imageUrl && !isUploading && (
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onChange(undefined);
            }}
            sx={{
              position: "absolute",
              top: 4,
              right: 4,
              backgroundColor: "rgba(0,0,0,0.55)",
              color: "white",
              "&:hover": { backgroundColor: "rgba(0,0,0,0.75)" },
            }}>
            <CloseIcon fontSize="small" />
          </IconButton>
        )}
      </Box>
      {helperText && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: "block" }}>
          {helperText}
        </Typography>
      )}
    </Box>
  );
};

export default SocialPreviewImagePicker;
