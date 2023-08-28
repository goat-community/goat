import { Box } from "@mui/material";
import React, { useState, useRef } from "react";
import type { DragEvent, ChangeEvent } from "react";

import { makeStyles } from "../lib/ThemeProvider";
import { FileUploadProgress } from "./DataDisplay";
import { Text } from "./theme";
import { Icon } from "./theme";

interface DropFieldProps {
  onContentAdded: (value: FileList) => void;
  onUploadFinish: () => void;
}

const DropFieldFileInput = (props: DropFieldProps) => {
  const { onContentAdded, onUploadFinish } = props;

  const { classes } = useStyles();

  // Refs
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Component States
  const [, setIsDragOver] = useState(false);
  const [file, setFile] = useState<FileList>();

  // Functions
  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(false);
    const files = event.dataTransfer?.files;
    if (files) {
      console.log("files");
      // Process the dropped files here
      setFile(files);
      onContentAdded(files);
    }
  };

  const handleFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      // Process the selected files here
      setFile(files);
      onContentAdded(files);
    }
  };

  const handleDropZoneClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <>
      {file ? (
        <FileUploadProgress onFinished={onUploadFinish} />
      ) : (
        <Box
          className={classes.dropZone}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleDropZoneClick}>
          <Box className={classes.iconWrapper}>
            <Icon
              iconId="file"
              wrapped="circle"
              bgVariant="focus"
              bgOpacity={0.12}
              className={classes.icon}
            />
          </Box>
          <Text typo="body 1" className={classes.textMessage}>
            <Text typo="body 1" color="focus">
              Click to upload
            </Text>{" "}
            or drag and drop
          </Text>
          <Box sx={{ display: "flex", justifyContent: "center", gap: "8px" }}>
            <Icon iconId="info" iconVariant="gray" size="small" />
            <Text typo="label 2" color="secondary" className={classes.supportedFormat}>
              Supported formats: geojson, shapefile, geopackage, geobuf, csv, xlsx, kml, mvt, wfs, binary,
              wms, xyz, wmts, mvt, csv, xlsx, json
            </Text>
          </Box>
          <input
            type="file"
            ref={fileInputRef}
            className={classes.fileInput}
            onChange={handleFileInputChange}
            accept=".geojson,.shp,.gpkg,.geobuf,.csv,.xlsx,.kml,.mvt,.wfs,.binary,.wms,.xyz,.wmts,.json"
          />
        </Box>
      )}
    </>
  );
};

const useStyles = makeStyles({ name: { DropFieldFileInput } })((theme) => ({
  dropZone: {
    border: `1px dashed ${theme.colors.palette.dark.main}30 `,
    borderRadius: 4,
    padding: theme.spacing(4),
    textAlign: "center",
    cursor: "pointer",
  },
  fileInput: {
    display: "none",
  },
  iconWrapper: {
    display: "flex",
    justifyContent: "center",
  },
  icon: {
    margin: "8px",
  },
  textMessage: {
    display: "flex",
    justifyContent: "center",
    gap: theme.spacing(1),
    margin: `${theme.spacing(2)}px 0px`,
  },
  supportedFormat: {
    fontSize: "13px",
    lineHeight: "14.4px",
    textAlign: "left",
    width: "248px",
  },
}));

export default DropFieldFileInput;
