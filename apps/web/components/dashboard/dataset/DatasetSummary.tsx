import { Divider, Grid, Link, Stack, Typography, useTheme } from "@mui/material";
import React from "react";
import ReactMarkdown from "react-markdown";

import { Icon } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import { type Layer, datasetMetadataAggregated } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

import { useGetMetadataValueTranslation } from "@/hooks/map/DatasetHooks";

import { METADATA_HEADER_ICONS } from "@/components/dashboard/catalog/CatalogDatasetCard";

interface DatasetSummaryProps {
  dataset: ProjectLayer | Layer;
}

const DatasetSummary: React.FC<DatasetSummaryProps> = ({ dataset }) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation(["common", "countries"]);
  const getMetadataValueTranslation = useGetMetadataValueTranslation();
  const metadataSummaryFields = [
    {
      field: "description",
      heading: t("metadata.headings.description"),
      noMetadataAvailable: t("metadata.no_metadata_available.description"),
      type: "markdown",
    },
    {
      field: "data_reference_year",
      heading: t("metadata.headings.data_reference_year"),
      noMetadataAvailable: t("metadata.no_metadata_available.data_reference_year"),
      type: "text",
    },
    {
      field: "lineage",
      heading: t("metadata.headings.lineage"),
      noMetadataAvailable: t("metadata.no_metadata_available.lineage"),
      type: "markdown",
    },
    {
      field: "positional_accuracy",
      heading: t("metadata.headings.positional_accuracy"),
      noMetadataAvailable: t("metadata.no_metadata_available.positional_accuracy"),
      type: "text",
    },
    {
      field: "attribute_accuracy",
      heading: t("metadata.headings.attribute_accuracy"),
      noMetadataAvailable: t("metadata.no_metadata_available.attribute_accuracy"),
      type: "text",
    },
    {
      field: "completeness",
      heading: t("metadata.headings.completeness"),
      noMetadataAvailable: t("metadata.no_metadata_available.completeness"),
      type: "text",
    },
    {
      field: "distributor_name",
      heading: t("metadata.headings.distributor_name"),
      noMetadataAvailable: t("metadata.no_metadata_available.distributor_name"),
      type: "text",
    },
    {
      field: "distributor_email",
      heading: t("metadata.headings.distributor_email"),
      noMetadataAvailable: t("metadata.no_metadata_available.distributor_email"),
      type: "email",
    },
    {
      field: "distribution_url",
      heading: t("metadata.headings.distribution_url"),
      noMetadataAvailable: t("metadata.no_metadata_available.distribution_url"),
      type: "url",
    },
    {
      field: "attribution",
      heading: t("metadata.headings.attribution"),
      noMetadataAvailable: t("metadata.no_metadata_available.attribution"),
      type: "text",
    },
  ];

  return (
    <>
      <Grid container justifyContent="flex-start" spacing={4}>
        <Grid item xs={12} sm={12} md={8} lg={9}>
          <Stack spacing={6}>
            {metadataSummaryFields.map(({ field, heading, noMetadataAvailable, type }) => (
              <Stack key={field}>
                <Typography variant="caption">{heading}</Typography>
                <Divider />
                {!dataset[field] && (
                  <Typography variant="body2" sx={{ fontStyle: "italic" }}>
                    {noMetadataAvailable}
                  </Typography>
                )}
                {type === "markdown" && dataset[field] && <ReactMarkdown>{dataset[field]}</ReactMarkdown>}
                {type === "email" && dataset[field] && (
                  <Link href={`mailto:${dataset[field]}`} target="_blank" rel="noopener noreferrer">
                    {dataset[field]}
                  </Link>
                )}
                {type === "url" && dataset[field] && (
                  <Link href={dataset[field]} target="_blank" rel="noopener noreferrer">
                    {dataset[field]}
                  </Link>
                )}
                {type === "text" && dataset[field] && <Typography>{dataset[field]}</Typography>}
              </Stack>
            ))}
          </Stack>
        </Grid>
        <Grid item xs={12} sm={12} md={4} lg={3} sx={{ pl: 0 }}>
          <Stack spacing={4}>
            {Object.keys(datasetMetadataAggregated.shape).map((key) => {
              return (
                <Stack key={key} width="100%" alignItems="start" justifyContent="start">
                  <Typography variant="caption">
                    {i18n.exists(`common:metadata.headings.${key}`)
                      ? t(`common:metadata.headings.${key}`)
                      : key}
                  </Typography>
                  <Stack spacing={2} alignItems="center" justifyContent="start" direction="row">
                    <Icon
                      iconName={METADATA_HEADER_ICONS[key]}
                      style={{ fontSize: 14 }}
                      htmlColor={theme.palette.text.secondary}
                    />
                    <Typography variant="body2" fontWeight="bold">
                      {getMetadataValueTranslation(key, dataset[key])}
                    </Typography>
                  </Stack>
                </Stack>
              );
            })}
          </Stack>
        </Grid>
      </Grid>
    </>
  );
};

export default DatasetSummary;
