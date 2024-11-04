import { Autocomplete, Checkbox, TextField, Typography } from "@mui/material";
import React, { useState } from "react";

const LayerMobile = () => {
  interface layerObject {
    value: string;
    label: string;
  }

  const [selectedOption, _setSelectedOption] = useState<layerObject[]>([]);

  const sampleLayers = [
    {
      label: "Cyclists - Accident Points (2016-2020)",
      value: "cyclistsAccident",
      selected: false,
    },
    {
      label: "Pedestrians - Accident Points (2016-2020)",
      value: "pedestrianAccident",
      selected: false,
    },
    {
      label: "Boundary",
      value: "boundary",
      selected: false,
    },
    {
      label: "Study Area",
      value: "studyArea",
      selected: false,
    },
    {
      label: "Buildings",
      value: "buildings",
      selected: false,
    },
  ];

  const getSelectedOptions = () => {
    const selectedOptions = sampleLayers.filter(
      (option) => selectedOption && selectedOption.some((vendor) => vendor.label === option.label)
    );

    return selectedOptions;
  };

  // const handleChange = (value: layerObject | layerObject[] | null) => {
  //   if (setSelectedOption && Array.isArray(value)) {
  //     setSelectedOption([
  //       ...selected,
  //       ...value.map((val) => {
  //         const newVal = val;
  //         newVal.selected = true;
  //         return newVal;
  //       }),
  //     ]);
  //   }
  // };

  return (
    <>
      <Typography variant="h6">Layers</Typography>
      <Autocomplete
        multiple
        options={sampleLayers}
        disableCloseOnSelect
        getOptionLabel={(option) => option.value}
        renderOption={(props, option, { selected }) => (
          <li {...props}>
            <Checkbox style={{ marginRight: 8 }} checked={selected} />
            {option.label}
          </li>
        )}
        fullWidth
        size="small"
        renderInput={(params) => (
          <TextField {...params} label="Checkboxes" value={[]} placeholder="Favorites" />
        )}
        value={getSelectedOptions()}
        renderTags={() => null}
      />
    </>
  );
};

export default LayerMobile;
