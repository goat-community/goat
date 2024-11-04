import { Box, Divider, IconButton, Link, Paper, Stack, Tooltip, Typography } from "@mui/material";
import { useState } from "react";
import { Popup } from "react-map-gl/maplibre";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import type { MapPopoverInfoProps } from "@/types/map/popover";

import { OverflowTypograpy } from "@/components/common/OverflowTypography";

interface RowProps {
  name: string;
  value: string;
}

const Row: React.FC<RowProps> = ({ name, value }) => {
  // Set 'url' to 'value' if it looks like a url
  let url = "";
  if (!url && value && typeof value === "string" && value.match(/^(http|www)/)) {
    url = value;
  }

  return (
    <tr>
      <td>
        <OverflowTypograpy
          variant="body2"
          tooltipProps={{
            placement: "top",
            arrow: true,
            enterDelay: 200,
          }}>
          {name}
        </OverflowTypograpy>
      </td>
      <td style={{ textAlign: "right" }}>
        <OverflowTypograpy
          variant="body2"
          fontWeight="bold"
          tooltipProps={{
            placement: "top",
            arrow: true,
            enterDelay: 200,
          }}>
          {url ? (
            <Link target="_blank" rel="noopener noreferrer" href={url}>
              {value}
            </Link>
          ) : (
            <>{value}</>
          )}
        </OverflowTypograpy>
      </td>
    </tr>
  );
};

interface ViewTableRowProps {
  name: string;
  onClick: () => void;
}

const ViewTableRow: React.FC<ViewTableRowProps> = ({ name, onClick }) => {
  const { t } = useTranslation("common");

  return (
    <tr>
      <td>
        <OverflowTypograpy
          variant="body2"
          tooltipProps={{
            placement: "top",
            arrow: true,
            enterDelay: 200,
          }}>
          {name}
        </OverflowTypograpy>
      </td>
      <td style={{ textAlign: "right" }}>
        <Tooltip
          placement="top"
          arrow
          title={t("view_property_data", {
            property: name,
          })}>
          <IconButton size="small" onClick={onClick}>
            <Icon iconName={ICON_NAME.TABLE} style={{ fontSize: 16 }} />
          </IconButton>
        </Tooltip>
      </td>
    </tr>
  );
};

interface DetailsViewType {
  property: string;
  data: Array<{ [key: string]: string }>;
}

const MapPopoverInfo: React.FC<MapPopoverInfoProps> = ({
  title,
  properties,
  jsonProperties,
  lngLat,
  onClose,
}) => {
  const [detailsView, setDetailsView] = useState<DetailsViewType | undefined>(undefined);
  return (
    <Popup
      onClose={onClose}
      longitude={lngLat[0]}
      latitude={lngLat[1]}
      closeButton={false}
      maxWidth={detailsView ? "500px" : "300px"}>
      <Box>
        <Paper elevation={0}>
          <Stack sx={{ px: 2, pt: 2 }} direction="row" alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={2} alignItems="center" sx={{ width: "90%" }}>
              <Icon iconName={ICON_NAME.LAYERS} style={{ fontSize: 16 }} />
              <Typography variant="body2" fontWeight="bold">
                {title}
              </Typography>
            </Stack>
            <IconButton onClick={onClose}>
              <Icon iconName={ICON_NAME.XCLOSE} style={{ fontSize: 16 }} />
            </IconButton>
          </Stack>
          <Divider sx={{ mb: 0 }} />
          <Box sx={{ maxHeight: "280px", overflowY: "auto" }}>
            {properties && !detailsView && (
              <table
                style={{
                  tableLayout: "fixed",
                  width: "100%",
                  padding: 5,
                }}>
                <tbody>
                  {Object.entries(properties).map(([key, value]) => (
                    <Row key={key} name={key} value={value} />
                  ))}
                  {
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    jsonProperties &&
                      Object.entries(jsonProperties).map(
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        ([key, _value]: [string, any]) => (
                          <ViewTableRow
                            key={key}
                            name={key}
                            onClick={() =>
                              setDetailsView({
                                property: key,
                                data: jsonProperties[key],
                              })
                            }
                          />
                        )
                      )
                  }
                </tbody>
              </table>
            )}
            {detailsView && (
              <Stack direction="column">
                <Stack direction="row" spacing={2} alignItems="center" sx={{ width: "90%" }}>
                  <IconButton
                    onClick={() => {
                      setDetailsView(undefined);
                    }}>
                    <Icon iconName={ICON_NAME.CHEVRON_LEFT} style={{ fontSize: 16 }} />
                  </IconButton>
                  <Typography variant="body2" fontWeight="bold">
                    {detailsView.property}
                  </Typography>
                </Stack>
                <Divider sx={{ mb: 0, mt: 0 }} />
                <table style={{ tableLayout: "fixed", padding: 5 }}>
                  <thead>
                    <tr style={{ padding: 10 }}>
                      {detailsView.data.length > 0 &&
                        Object.keys(detailsView.data[0]).map((key, index) => (
                          <th key={index} style={{ paddingRight: 4 }}>
                            {key}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody>
                    {detailsView.data.length > 0 &&
                      detailsView.data.map((item, index) => (
                        <tr key={index}>
                          {Object.entries(item).map(([key, value]) => (
                            <td style={{ paddingRight: 10 }} key={key}>
                              {value}
                            </td>
                          ))}
                        </tr>
                      ))}
                  </tbody>
                </table>
              </Stack>
            )}
          </Box>
        </Paper>
      </Box>
    </Popup>
  );
};

export default MapPopoverInfo;
