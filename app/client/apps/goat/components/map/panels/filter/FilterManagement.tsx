"use client";

import { useGetKeys } from "@/hooks/map/FilteringHooks";
import { comparerModes } from "@/public/assets/data/comparers_filter";
import type { ComparerMode, LayerPropsMode } from "@/types/map/filtering";
// import { Dayjs } from "dayjs";
import React from "react";
import { useState } from "react";

import { SelectField } from "@p4b/ui/components/Inputs";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

import FilterOptionField from "./FilterOptionField";
import { Card, CardMedia } from "@p4b/ui/components/Surfaces";
import { ICON_NAME } from "@p4b/ui/components/Icon";
import { Icon } from "@p4b/ui/components/Icon";
import { useTheme } from "@/lib/theme";
import { Text } from "@/lib/theme";
import { Box } from "@mui/material";
import { Button } from "@p4b/ui/components/theme";
import { v4 } from "uuid";
import { Chip } from "@/components/common/Chip";

// main component
const FilterManagement = () => {
  const sampleLayerID = "user_data.8c4ad0c86a2d4e60b42ad6fb8760a76e";

  const { keys } = useGetKeys({ layer_id: sampleLayerID });
  // const [date, setDate] = useState<Dayjs | null>(null);
  const [attributeSelected, setAttributeSelected] = useState<string | string[]>("");
  const [comparerSelected, setComparerSelected] = useState<string | string[]>("");
  // const [addExpressionStatus, setAddExpressionStatus] = useState(false);
  const [expressions, setExpressions] = useState<
    | {
        attribute: LayerPropsMode | null;
        expression: ComparerMode | null;
        value: (string | number | number[]) | null;
      }[]
    | null
  >(null);

  const theme = useTheme();
  const { classes } = useStyles();

  function getFeatureAttribute(type: string | string[]) {
    const valueToFilter = keys.filter((key) => key.name === type);
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

  function createExpression() {
    if (expressions) {
      setExpressions([
        ...expressions,
        {
          attribute: null,
          expression: null,
          value: null,
        },
      ]);
    } else {
      setExpressions([
        {
          attribute: null,
          expression: null,
          value: null,
        },
      ]);
    }
  }

  return (
    <div>
      <Card>
        <div className={classes.ContentHeader}>
          <Icon iconName={ICON_NAME.STAR} htmlColor={`${theme.colors.palette.focus.main}4D`} />
          <Text typo="body 2" className={classes.headerText}>
            @content_label
          </Text>
        </div>
      </Card>
      {expressions ? (
        expressions.map((_, indx) => (
          <>
            <Box key={v4()}>
              <Box className={classes.expressionHeader}>
                <Text typo="body 2">Expression</Text>
                <Icon iconName={ICON_NAME.ELLIPSIS} />
              </Box>
              <SelectField
                className={classes.fields}
                options={keys.map((key) => ({ name: key.name, value: key.name }))}
                label="Select attribute"
                size="small"
                updateChange={setAttributeSelected}
              />
              <SelectField
                className={classes.fields}
                options={
                  attributeSelected.length
                    ? comparerModes[getFeatureAttribute(attributeSelected)].map((attr: ComparerMode) => ({
                        name: attr.label,
                        value: attr.value,
                      }))
                    : [
                        {
                          name: "",
                          value: "",
                        },
                      ]
                }
                label="Select an expression"
                size="small"
                disabled={attributeSelected.length ? false : true}
                updateChange={setComparerSelected}
              />
              {attributeSelected.length ? (
                <>
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
            </Box>
            {indx + 1 !== expressions.length ? (
              <Box className={classes.andExpression}>
                <Chip label="And" />
              </Box>
            ) : null}
          </>
        ))
      ) : (
        <Box sx={{ marginTop: `${theme.spacing(4)}px` }}>
          <Card
            aboveDivider={
              <CardMedia
                className={classes.cardMediaImage}
                src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s"
              />
            }>
            <div className={classes.CardWrapper}>
              <Text typo="body 1">Filter your data</Text>
              <Text className={classes.CardDescription} typo="label 2">
                Perform targeted data analysis. Filter layers, apply an expression and narrow down data
                displayed. Sort data and hide data that does not match your criteria. Learn more
              </Text>
            </div>
          </Card>
        </Box>
      )}
      <Button
        // disabled={addExpressionStatus}
        className={classes.expressionButton}
        onClick={createExpression}>
        Add Expression
      </Button>
      {/* <SelectField
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
      Comparers to use for filtering */}
    </div>
  );
};

const useStyles = makeStyles({ name: { FilterManagement } })((theme) => ({
  ContentHeader: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    padding: `${theme.spacing(2)}px ${theme.spacing(3)}px`,
  },
  headerText: {
    width: "fit-content",
  },
  cardMediaImage: {
    height: "56px",
  },
  CardDescription: {
    fontSize: "11px",
    lineHeight: "175%",
    fontStyle: "italic",
    color: theme.colors.palette.light.greyVariant3,
    paddingTop: theme.spacing(3),
    paddingBottom: theme.spacing(2),
  },
  CardWrapper: {
    padding: `${theme.spacing(2)}px ${theme.spacing(3)}px`,
  },
  expressionButton: {
    width: "100%",
    marginTop: theme.spacing(4),
  },
  expressionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: theme.spacing(4),
    padding: "9.5px",
  },
  andExpression: {
    display: "flex",
    justifyContent: "center",
    margin: `${theme.spacing(4)}px 0`,
  },
  fields: {
    margin: `${theme.spacing(2)}px 0`,
  }
}));

export default FilterManagement;
