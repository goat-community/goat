"use client";

import { useGetKeys } from "@/hooks/map/FilteringHooks";
import { comparerModes } from "@/public/assets/data/comparers_filter";
import type { ComparerMode } from "@/types/map/filtering";
// import { Dayjs } from "dayjs";
import React from "react";
import { useState } from "react";

import { SelectField } from "@p4b/ui/components/Inputs";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

import FilterOptionField from "./FilterOptionField";

// main component
const FilterManagement = () => {
  const sampleLayerID = "user_data.8c4ad0c86a2d4e60b42ad6fb8760a76e";

  const { keys } = useGetKeys({ layer_id: sampleLayerID });
  // const [date, setDate] = useState<Dayjs | null>(null);
  const [attributeSelected, setAttributeSelected] = useState<string | string[]>("");
  const [comparerSelected, setComparerSelected] = useState<string | string[]>("");

  // const { classes } = useStyles();

  function getFeatureAttribute(type: string | string[]) {
    const valueToFilter = keys.filter((key) => key.name === type);
    console.log(keys, valueToFilter[0].type)
    if (valueToFilter[0].type === "string") {
      return "text";
    }
    return valueToFilter[0].type;
  }

  function getComparer(type: string | string[]) {
    return comparerModes[getFeatureAttribute(attributeSelected)].filter(
      (compAttribute) => type === compAttribute.value
    );
  }

  return (
    <div>
      <div>card</div>
      <SelectField
        options={keys.map((key) => ({ name: key.name, value: key.name }))}
        label="Select Attribute"
        size="small"
        updateChange={setAttributeSelected}
      />
      {attributeSelected.length ? (
        <>
          <SelectField
            options={comparerModes[getFeatureAttribute(attributeSelected)].map((attr: ComparerMode) => ({
              name: attr.label,
              value: attr.value,
            }))}
            label="Select Attribute"
            size="small"
            updateChange={setComparerSelected}
          />
          {comparerSelected.length ? (
            <FilterOptionField
              comparer={attributeSelected.length ? [...getComparer(comparerSelected)][0] : null}
              prop={typeof attributeSelected === "string" ? attributeSelected : ""}
              layer_id={sampleLayerID}
            />
          ) : (
            <p>Chose a comparer</p>
          )}
        </>
      ) : (
        <p>Chose an attribute</p>
      )}
      Comparers to use for filtering
    </div>
  );
};

const useStyles = makeStyles({ name: { FilterManagement } })(() => ({
  root: {},
}));

export default FilterManagement;
