// Copyright (c) 2020 GitHub user u/garronej
import { Box } from "@mui/material";
import { forwardRef, memo } from "react";
import type { Equals } from "tsafe";
import { assert } from "tsafe/assert";

import { makeStyles } from "../../lib/ThemeProvider";
import LinearProgress from "../LinearProgress";
import { Text, IconButton, Icon } from "../theme";

export type FileUploadProgressProps = {
  className?: string;
  onFinished: () => void;
  finished?: boolean;
};

export const FileUploadProgress = memo(
  forwardRef<HTMLElement, FileUploadProgressProps>((props) => {
    const {
      className,
      onFinished,
      finished = false,
      //For the forwarding, rest should be empty (typewise)
      ...rest
    } = props;

    //For the forwarding, rest should be empty (typewise),
    // eslint-disable-next-line @typescript-eslint/ban-types
    assert<Equals<typeof rest, {}>>();

    const { classes } = useStyles();

    return (
      <Box className={classes.container}>
        <Box>
          <Icon iconId="file" wrapped="circle" bgVariant="focus" bgOpacity={0.12} className={classes.icon} />
        </Box>
        <Box sx={{ width: "228px" }}>
          <Text typo="label 2">document _file_name.pdf</Text>
          <Text typo="label 2" color="secondary" className={classes.dataInfo}>
            <Text typo="label 2" color="secondary">
              100kb
            </Text>{" "}
            <Text typo="label 2" color="secondary">
              •
            </Text>
            <Text typo="label 2" color="secondary">
              {finished ? "Complete" : "Loading"}
            </Text>
          </Text>
          {finished ? (
            <LinearProgress finished={onFinished} defaultValue={100} />
          ) : (
            <LinearProgress finished={onFinished} />
          )}
        </Box>
        <Box>
          <IconButton type="submit" iconId="close" size="small" iconVariant="grey" />
        </Box>
      </Box>
    );
  })
);

const useStyles = makeStyles({ name: { FileUploadProgress } })((theme) => ({
  container: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    gap: theme.spacing(3),
    padding: theme.spacing(3),
  },
  content: {
    width: "228px",
  },
  icon: {
    margin: "8px",
  },
  dataInfo: {
    marginBottom: theme.spacing(3),
    display: "flex",
    gap: theme.spacing(2),
  },
}));
