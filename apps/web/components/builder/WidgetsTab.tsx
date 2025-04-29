import { DragOverlay, useDndMonitor, useDraggable } from "@dnd-kit/core";
import {
  Bookmark as BookmarksIcon,
  Category as CategoriesIcon,
  Comment as CommentsIcon,
  HorizontalRule as DividerIcon,
  List as FeatureListIcon,
  FilterList as FilterIcon,
  NearMe as FindNearestIcon,
  BarChart as HistogramIcon,
  Image as ImageIcon,
  Layers as LayersIcon,
  Functions as NumbersIcon,
  PieChart as PieChartIcon,
  Search as SearchIcon,
  TableChart as TableIcon,
  TextFields as TextIcon,
  Timeline as TimelineIcon,
} from "@mui/icons-material";
import { Box, Divider, Grid, InputAdornment, Stack, TextField, Typography, styled } from "@mui/material";
import React, { useMemo, useState } from "react";

import { createSnapToCursorModifier } from "@/lib/utils/dnd-modifier";

const iconMap = {
  search: SearchIcon,
  layers: LayersIcon,
  bookmarks: BookmarksIcon,
  comments: CommentsIcon,
  filter: FilterIcon,
  table: TableIcon,
  numbers: NumbersIcon,
  featureList: FeatureListIcon,
  timeline: TimelineIcon,
  findNearest: FindNearestIcon,
  categories: CategoriesIcon,
  histogram: HistogramIcon,
  pieChart: PieChartIcon,
  text: TextIcon,
  image: ImageIcon,
  divider: DividerIcon,
};

type MenuItem = {
  id: string; // Unique ID for each item (required for dnd-kit)
  label: string;
  icon: keyof typeof iconMap;
  action?: () => void;
};

type MenuSection = {
  title: string;
  items: MenuItem[];
};

interface WidgetTabProps {
  sections: MenuSection[];
}

const SquareItem = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: 64,
  width: 64,
  borderRadius: 8,
  border: `1px solid ${theme.palette.divider}`,
  "&:hover": {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.hover,
  },
}));

const CardTile = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "flex-start",
  height: 64,
  width: 160,
  borderRadius: 8,
  border: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[4], // Add elevation (shadow)
  padding: theme.spacing(3), // Add some padding
}));

const Label = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(0.5),
  textAlign: "center",
  maxWidth: 64,
  wordWrap: "break-word",
  overflowWrap: "break-word",
  whiteSpace: "normal",
}));

const CardTileLabel = styled(Typography)(({ theme }) => ({
  marginLeft: theme.spacing(1.5), // Add spacing between icon and label
  textAlign: "left",
  whiteSpace: "nowrap", // Prevent label from wrapping
  overflow: "hidden",
  textOverflow: "ellipsis", // Add ellipsis for long labels
}));

function Draggable(props) {
  const Element = props.element || "div";
  const { attributes, listeners, setNodeRef } = useDraggable({
    id: props.id,
  });

  return (
    <Element ref={setNodeRef} {...listeners} {...attributes}>
      {props.children}
    </Element>
  );
}

interface DraggableItemProps {
  item: MenuItem;
  isDragging?: boolean;
}

const DraggableItem = ({ item, isDragging = false }: DraggableItemProps) => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", cursor: "grab" }}>
      {isDragging ? (
        <CardTile>
          {iconMap[item.icon] && React.createElement(iconMap[item.icon], { fontSize: "medium" })}
          <CardTileLabel variant="body2">{item.label}</CardTileLabel>
        </CardTile>
      ) : (
        <>
          <SquareItem onClick={item.action}>
            {iconMap[item.icon] && React.createElement(iconMap[item.icon], { fontSize: "medium" })}
          </SquareItem>
          <Label variant="caption">{item.label}</Label>
        </>
      )}
    </Box>
  );
};

const WidgetTab = ({ sections }: WidgetTabProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeId, setActiveId] = useState(null);
  const filteredSections = sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => item.label.toLowerCase().includes(searchTerm.toLowerCase())),
    }))
    .filter((section) => section.items.length > 0);

  function handleDragStart(event) {
    setActiveId(event.active.id);
  }

  function handleDragEnd() {
    setActiveId(null);
  }

  useDndMonitor({
    onDragStart: handleDragStart,
    onDragEnd: handleDragEnd,
  });

  const activeItem: MenuItem | undefined = useMemo(() => {
    return sections.flatMap((section) => section.items).find((item) => item.id === activeId);
  }, [sections, activeId]);

  return (
    <>
      <Stack direction="column" height="100%" width="100%">
        <TextField
          fullWidth
          placeholder="Search..."
          sx={{ p: 3 }}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          size="small"
        />
        {/* Scrollable Content */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto", // Enable vertical scrolling
            height: "100%",
          }}>
          <Stack spacing={4} sx={{ p: 3 }}>
            {filteredSections.map((section) => (
              <Box key={section.title}>
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: "bold" }}>
                  {section.title}
                </Typography>
                <Divider sx={{ mt: 0, mb: 4 }} />
                <Grid container spacing={4}>
                  {section.items.map((item) => (
                    <Grid item xs={3} key={item.id}>
                      <Draggable id={item.id}>
                        <DraggableItem item={item} />
                      </Draggable>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            ))}
          </Stack>
        </Box>
      </Stack>
      <DragOverlay dropAnimation={null} modifiers={[createSnapToCursorModifier("topCenter")]}>
        {activeItem ? <DraggableItem item={activeItem} isDragging={true} /> : null}
      </DragOverlay>
    </>
  );
};

export default WidgetTab;
