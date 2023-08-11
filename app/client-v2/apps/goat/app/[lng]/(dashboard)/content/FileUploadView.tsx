import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Typography } from "@mui/material";
import Avatar from "@mui/material/Avatar";
import * as React from "react";

import Box from "@p4b/ui/components/Box";
import Link from "@p4b/ui/components/Link";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

export default function FileUploadView() {
  const { classes } = useStyles();
  return (
    <Box className={classes.root}>
      <Avatar className={classes.avatar}>
        <UploadFileIcon sx={{ color: "#2BB381" }} />
      </Avatar>
      <Typography>
        <Link href="#">Click to upload</Link> or drag and drop
      </Typography>
      <Typography className={classes.supportedFormats}>
        Supported formats: geojson, shapefile, geopackage, geobuf, csv, xlsx, kml, mvt, wfs, binary, wms, xyz,
        wmts, mvt, csv, xlsx, json
      </Typography>
    </Box>
  );
}

const useStyles = makeStyles({ name: { FileUploadView } })(() => ({
  root: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  supportedFormats: {
    fontSize: "12px",
    marginTop: "10px",
  },
  avatar: {
    marginBottom: "16px",
    backgroundColor: "#2BB3811F",
  },
}));
