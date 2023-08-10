import { loadLayerService } from "@/lib/services/dashboard";
import { Button } from "@mui/material";
import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import * as React from "react";
import { useState } from "react";

import { CircularProgress } from "@p4b/ui/components/CircularProgress";
import { CollapseAlert } from "@p4b/ui/components/CollapseAlert";
import { Divider } from "@p4b/ui/components/DataDisplay";
import { TextField } from "@p4b/ui/components/Inputs";
import Link from "@p4b/ui/components/Link";
import RadioButtonsGroup from "@p4b/ui/components/RadioButtonsGroup";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface AddLayerManagementProps {
  selectedFolder: object;
  setAddLayerMode: (boolean) => void;
  addLayer: (value: object) => void;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
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
  const [loadedLayerData, setLoadedLayerData] = useState<object | null>(null);
  const [errorOpen, setErrorOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const resetAddLayerHandler = () => {
    setLoadedLayerData(null);
    setUrl("");
    setRadioButtonValue("Imagery");
  };

  const addLayerHandler = async () => {
    const body = {
      folder_id: selectedFolder.id,
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

  return (
    <Box sx={{ width: "100%" }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={handleChange} aria-label="basic tabs example">
          <Tab sx={{ width: "50%" }} label="INTERNAL" {...a11yProps(0)} />
          <Tab sx={{ width: "50%" }} label="EXTERNAL" {...a11yProps(1)} />
        </Tabs>
      </Box>
      <CustomTabPanel value={tabValue} index={0}>
        Item One
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
            <Box
              sx={{
                display: "flex",
                justifyContent: "flex-end",
                marginY: "10px",
              }}>
              <Button onClick={resetAddLayerHandler}>RESET</Button>
              <Button onClick={addLayerHandler}>ADD</Button>
            </Box>
          </Box>
        ) : (
          <>
            {loading ? (
              <Box sx={{ display: "flex", justifyContent: "center" }}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <Typography variant="body1">Paste the URL here:</Typography>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    width: "100%",
                    gap: "10px",
                    margin: "10px 0",
                  }}>
                  <TextField sx={{ width: "100%" }} defaultValue={url} setValueData={setUrl} />
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
