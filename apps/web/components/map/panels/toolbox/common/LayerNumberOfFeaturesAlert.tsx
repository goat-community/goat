import { Alert, Typography } from "@mui/material";
import React from "react";

interface LayerNumberOfFeaturesAlertProps {
  maxFeatures: number;
  currentFeatures: number;
  texts: {
    maxFeaturesText: string;
    filterLayerFeaturesActionText: string;
  };
}

const LayerNumberOfFeaturesAlert: React.FC<LayerNumberOfFeaturesAlertProps> = ({
  maxFeatures,
  currentFeatures,
  texts,
}) => {
  return (
    <Alert variant="outlined" severity={currentFeatures > maxFeatures ? "error" : "info"} sx={{ mb: 4 }}>
      <Typography variant="caption" color="inherit" fontWeight="bold">
        {`${texts.maxFeaturesText} ${currentFeatures} / ${maxFeatures}`}
      </Typography>
      <br />
      {currentFeatures > maxFeatures && (
        <Typography variant="caption" color="inherit">
          {texts.filterLayerFeaturesActionText}
        </Typography>
      )}
    </Alert>
  );
};

export default LayerNumberOfFeaturesAlert;
