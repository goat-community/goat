import FileUploadView from "@/app/[lng]/(dashboard)/content/FileUploadView";
import { loadLayerService } from "@/lib/services/dashboard";
import { supportedFileTypes } from "@/lib/utils/helpers";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Button } from "@mui/material";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import * as React from "react";
import { useState } from "react";
import { FileUploader } from "react-drag-drop-files";

import { CircularProgress } from "@p4b/ui/components/CircularProgress";
import { CollapseAlert } from "@p4b/ui/components/CollapseAlert";
import { Divider } from "@p4b/ui/components/DataDisplay";
import { TextField } from "@p4b/ui/components/Inputs";
import Link from "@p4b/ui/components/Link";
import RadioButtonsGroup from "@p4b/ui/components/RadioButtonsGroup";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {ISelectedFolder} from "@/types/dashboard/content";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// todo: check this if it's correct

interface LoadedLayerDataProps {
  link: string;
}

interface FileProps {
  name: string;
}

interface AddLayerManagementProps {
  selectedFolder: ISelectedFolder | null;
  setAddLayerMode: (value: boolean) => void;
  addLayer: (value: object) => void;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  const { classes } = useStyles();

  return (
    <div
      className={classes.dropzone}
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}>
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    "aria-controls": `simple-tabpanel-${index}`,
  };
}

const radioButtonLabels = [
  {
    value: "Imagery",
    desc: "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis ",
  },
  {
    value: "Vector",
    desc: "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis ",
  },
];

export default function AddLayerManagement(props: AddLayerManagementProps) {
  const { selectedFolder, setAddLayerMode, addLayer } = props;

  const [tabValue, setTabValue] = useState<number>(0);
  const [radioButtonValue, setRadioButtonValue] = useState<string>("Imagery");
  const [url, setUrl] = useState<string>("");
  const [loadedLayerData, setLoadedLayerData] = useState<LoadedLayerDataProps | null>(null);
  const [errorOpen, setErrorOpen] = useState<boolean>(false);
  const [uploadErrorOpen, setUploadErrorOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<FileProps | null>(null);

  const { classes } = useStyles();

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    console.log('handleChange event', event)
    setTabValue(newValue);
  };

  const resetAddLayerHandler = () => {
    setLoadedLayerData(null);
    setUploadErrorOpen(false);
    setSelectedFile(null);
    setUrl("");
    setRadioButtonValue("Imagery");
  };

  const addLayerHandler = async () => {
    //todo change
    const body = {
      folder_id: selectedFolder?.id,
      name: "Layer name",
      description: "Layer description",
      tags: ["tag1", "tag2"],
      thumbnail_url: url,
      data_source: "data_source plan4better example",
      data_reference_year: 2020,
      type: "table",
    };

    addLayer(body);
    resetAddLayerHandler();
    setAddLayerMode(false);
  };

  const loadUrlHandler = async () => {
    setLoading(true);

    //todo check and add validations
    const res = await loadLayerService(url);

    if (!res) {
      setErrorOpen(true);
    } else {
      setLoadedLayerData(res);
    }

    setLoading(false);
  };

  const dragDropHandler = (file: React.SetStateAction<FileProps>) => {
    setLoading(true);

    const fileNameParts = file.name.split(".");
    const fileExtension = fileNameParts[fileNameParts.length - 1].toLowerCase();

    if (!supportedFileTypes.includes(fileExtension)) {
      setUploadErrorOpen(true);
      setLoading(false);
      return;
    } else {
      setSelectedFile(file);
    }
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <Box className={classes.root}>
      <Box className={classes.tabsContainer}>
        <Tabs value={tabValue} onChange={handleChange} aria-label="basic tabs example">
          <Tab className={classes.tab} label="INTERNAL" {...a11yProps(0)} />
          <Tab className={classes.tab} label="EXTERNAL" {...a11yProps(1)} />
        </Tabs>
      </Box>
      <CustomTabPanel value={tabValue} index={0}>
        {loading ? (
          <Box className={classes.loading}>
            <CircularProgress />
          </Box>
        ) : selectedFile ? (
          <Box>
            <Box className={classes.fileInfo}>
              <Avatar sx={{ backgroundColor: "#2BB3811F" }}>
                <UploadFileIcon sx={{ color: "#2BB381" }} />
              </Avatar>
              <Typography>{selectedFile.name}</Typography>
            </Box>

            <Box className={classes.buttonsWrapper}>
              <Button onClick={resetAddLayerHandler}>RESET</Button>
              <Button onClick={addLayerHandler}>ADD</Button>
            </Box>
          </Box>
        ) : (
          <FileUploader
            handleChange={dragDropHandler}
            name="file"
            classes="dropzone-input"
            /* eslint-disable react/no-children-prop */
            children={<FileUploadView />}
          />
        )}
        <CollapseAlert
          open={uploadErrorOpen}
          setOpen={setUploadErrorOpen}
          severity="error"
          title="Error"
          description="Make sure you are trying to load a supported file: geojson, shapefile, geopackage, geobuf, csv, xlsx, kml, mvt, wfs, binary, wms, xyz, wmts, mvt, csv, xlsx, json"
        />
      </CustomTabPanel>
      <CustomTabPanel value={tabValue} index={1}>
        <RadioButtonsGroup
          value={radioButtonValue}
          setValue={setRadioButtonValue}
          radioLabels={radioButtonLabels}
        />
        <Divider lineColor="#2BB381" width="100%" color="main" />

        {loadedLayerData ? (
          <Box>
            <Link target="_blank" href={loadedLayerData?.link}>
              {loadedLayerData?.link}
            </Link>

            <Box className={classes.buttonsWrapper}>
              <Button onClick={resetAddLayerHandler}>RESET</Button>
              <Button onClick={addLayerHandler}>ADD</Button>
            </Box>
          </Box>
        ) : (
          <>
            {loading ? (
              <Box className={classes.loading}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <Typography variant="body1">Paste the URL here:</Typography>
                <Box className={classes.loadUrlWrapper}>
                  <TextField className={classes.width100} defaultValue={url} setValueData={setUrl} />
                  <Button type="button" variant="outlined" disabled={!url} onClick={loadUrlHandler}>
                    Load
                  </Button>
                </Box>
              </>
            )}
          </>
        )}
        <CollapseAlert
          open={errorOpen}
          setOpen={setErrorOpen}
          severity="error"
          title="URL not supported"
          description="Make sure to write an available link that contains all the capabilities!"
        />
      </CustomTabPanel>
    </Box>
  );
}

const useStyles = makeStyles()(() => ({
  root: {
    width: "100%",
  },
  tabsContainer: {
    borderBottom: 1,
    borderColor: "divider",
  },
  tab: {
    width: "50%",
  },
  fileInfo: {
    display: "flex",
    alignItems: "center",
    overflow: "hidden",
    gap: "20px",
  },
  loading: {
    display: "flex",
    justifyContent: "center",
  },
  loadUrlWrapper: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    width: "100%",
    gap: "10px",
    margin: "10px 0",
  },
  buttonsWrapper: {
    display: "flex",
    justifyContent: "flex-end",
    marginY: "10px",
  },
  width100: {
    width: "100%",
  },
  dropzone: {
    textAlign: "center",
    padding: "24px 5px",
    border: "3px dashed #eeeeee",
    backgroundColor: "#fafafa",
    color: "#bdbdbd",
    cursor: "pointer",
    marginBottom: "20px",
    height: "185px",
    display: "flex",
    flexDirection: "column",
  },
}));
