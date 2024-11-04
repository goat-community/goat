import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { DragIndicator } from "@mui/icons-material";
import { Card, Grid, Stack, useTheme } from "@mui/material";
import React from "react";

import { DragHandle } from "@/components/common/DragHandle";

type SortableTileProps = {
  id: number | string;
  active: boolean;
  onClick: () => void;
  actions?: React.ReactNode;
  body: React.ReactNode;
  isSortable?: boolean;
};

export function SortableTile(props: SortableTileProps) {
  const theme = useTheme();
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: props.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition: `${transition}, border-color 0.2s ease-in-out`,
  };

  return (
    <Card
      onClick={props.onClick}
      sx={{
        cursor: "pointer",
        my: 2,
        pr: 0,
        pl: 1,
        borderLeft: props.active ? `5px ${theme.palette.primary.main} solid` : "5px transparent solid",
        py: 2,
        ":hover": {
          boxShadow: 6,
          ...(!props.active && {
            borderLeft: `5px ${theme.palette.text.secondary} solid`,
          }),
          "& div, & button": {
            opacity: 1,
          },
        },
      }}
      key={props.id}
      ref={setNodeRef}
      style={style}>
      <Grid container alignItems="center" spacing={2}>
        <Grid item xs={1}>
          {props.isSortable && (
            <DragHandle {...attributes} listeners={listeners}>
              <DragIndicator fontSize="small" />
            </DragHandle>
          )}
        </Grid>
        <Grid item xs={8} zeroMinWidth>
          <Stack spacing={1}>{props.body}</Stack>
        </Grid>
        <Grid item xs={3}>
          {props.actions}
        </Grid>
      </Grid>
    </Card>
  );
}
