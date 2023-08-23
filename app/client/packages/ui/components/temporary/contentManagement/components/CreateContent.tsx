import React, { useEffect, useRef, useState } from "react";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { Divider } from "../../../DataDisplay";
import { FileUploadProgress } from "../../../DataDisplay";
import DropFieldFileInput from "../../../DropFieldFileInput";
import { SelectField, TextField } from "../../../Inputs";
import Stepper from "../../../Stepper";
import { Button, Text } from "../../../theme";

interface CreateContentProps {
  modalState: (value: boolean) => void;
}

const CreateContent = (props: CreateContentProps) => {
  const { modalState } = props;

  const { classes } = useStyles();

  // refs
  const stepperElem = useRef<{ handleComplete: () => void } | null>(null);

  // Input related
  const [uploadType, setUploadType] = useState<string | string[]>("");
  const [urlValue, setUrlValue] = useState("");
  const [saveFormat, setSaveFormat] = useState<string | string[]>("");
  const [uploadFile, setUploadFile] = useState<FileList>();
  const [progressUpload, setProgressUpload] = useState<boolean>(false);

  // dumb data
  const layerTypes = [
    {
      name: "URL",
      value: "url",
    },
    {
      name: "Shapefile",
      value: "shapefile",
    },
    {
      name: "Geopackage",
      value: "geopackage",
    },
    {
      name: "Geobuf",
      value: "geobuf",
    },
    {
      name: "CSV",
      value: "csv",
    },
    {
      name: "XLSX",
      value: "xlsx",
    },
    {
      name: "KML",
      value: "kml",
    },
  ];

  // Add Content steps in case the chosen layer type is URL
  let steps = [
    {
      label: "Choose format",
      status: "active",
      child: (
        <div>
          <Text typo="body 1">Chose Layer Type:</Text>
          <SelectField
            className={classes.selectInput}
            options={layerTypes}
            label="Chose Format"
            size="small"
            updateChange={setUploadType}
          />
          <Text color="secondary" typo="label 2" className={classes.descriptionText}>
            Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
            massa. Cum sociis natoque penatibus et magnis{" "}
          </Text>
        </div>
      ),
    },
    {
      label: "Load content",
      status: "active",
      child: (
        <div>
          <Text typo="body 1">Paste the URL here:</Text>
          <div className={classes.FormInputWrapper}>
            <TextField
              onValueBeingTypedChange={({ value }) => setUrlValue(value)}
              size="small"
              label=""
              className={classes.FormInput}
            />
            <Button variant="noBorder" onClick={loadUrl} disabled={urlValue.length > 4 ? false : true}>
              LOAD
            </Button>
          </div>
          <Text color="secondary" typo="label 2" className={classes.descriptionText}>
            Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
            massa. Cum sociis natoque penatibus et magnis{" "}
          </Text>
        </div>
      ),
    },
    {
      label: "Store",
      status: "active",
      child: (
        <div>
          <div className={classes.urlPreview}>
            <img
              src="https://i.postimg.cc/GpvYCgx9/geoportal-min.png"
              alt="geoportal"
              className={classes.image}
            />
            <Text typo="body 2">GeoPortal Title XYZ</Text>
            <Text typo="label 2" className={classes.textLink} color="secondary">
              {urlValue}
            </Text>
          </div>
          <Divider width="100%" color="gray" />
          <div>
            <Text typo="body 1">Choose a storing format:</Text>
            <SelectField
              className={classes.selectInput}
              options={layerTypes}
              label="Chose Format"
              size="small"
              updateChange={setSaveFormat}
            />
            <Text color="secondary" typo="label 2" className={classes.descriptionText}>
              Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.
              Aenean massa. Cum sociis natoque penatibus et magnis{" "}
            </Text>
          </div>
        </div>
      ),
    },
  ];

  // Add content steps in case we chose to import via local types (type !== url)
  const uploadLocallySteps = [
    {
      label: "Choose format",
      status: "active",
      child: (
        <div>
          <Text typo="body 1">Chose Layer Type:</Text>
          <SelectField
            className={classes.selectInput}
            options={layerTypes}
            label="Chose Format"
            size="small"
            updateChange={setUploadType}
          />
          <Text color="secondary" typo="label 2" className={classes.descriptionText}>
            Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
            massa. Cum sociis natoque penatibus et magnis{" "}
          </Text>
        </div>
      ),
    },
    {
      label: "Load content",
      status: "active",
      child: (
        <div>
          <DropFieldFileInput onContentAdded={setUploadFile} onUploadFinish={() => setProgressUpload(true)} />
        </div>
      ),
    },
    {
      label: "Store",
      status: "active",
      child: (
        <div>
          <FileUploadProgress onFinished={() => console.log("finished")} finished={true} />
        </div>
      ),
    },
  ];

  useEffect(() => {
    if (uploadType) {
      if (uploadType !== "url") {
        const newSteps = steps.slice(0, -2);
        steps = [...newSteps, ...uploadLocallySteps];
      }
      completeStep();
    }
  }, [uploadType, progressUpload]);

  //functions
  const simpleActions = (
    <div className={classes.buttons}>
      <Button variant="noBorder" onClick={() => modalState(false)}>
        CANCEL
      </Button>
      {saveFormat.length || progressUpload ? (
        <Button variant="noBorder" onClick={() => modalState(false)}>
          ADD
        </Button>
      ) : null}
    </div>
  );

  function loadUrl() {
    if (urlValue) {
      completeStep();
    }
  }

  function completeStep() {
    if (stepperElem.current !== null && stepperElem.current !== undefined) {
      stepperElem.current.handleComplete();
    }
  }

  return (
    <div>
      <Stepper
        steps={uploadType === "url" ? steps : uploadLocallySteps}
        ref={stepperElem}
        customActions={simpleActions}
        className={classes.stepper}
      />
    </div>
  );
};

const useStyles = makeStyles({ name: { Stepper } })((theme) => ({
  stepper: {
    paddingBottom: theme.spacing(3),
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
  },
  selectInput: {
    margin: `${theme.spacing(3)}px 0px`,
  },
  stepText: {
    fontSize: "14px",
  },
  descriptionText: {
    fontStyle: "italic",
  },
  FormInputWrapper: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
  },
  FormInput: {
    flexGrow: "1",
    margin: `${theme.spacing(3)}px 0px`,
  },
  image: {
    boxShadow: theme.shadows[2],
  },
  textLink: {
    fontStyle: "italic",
  },
  urlPreview: {
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(3),
  },
}));

export default CreateContent;
