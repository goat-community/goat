"use client";

import { Table as MUITable } from "@mui/material";
import Paper from "@mui/material/Paper";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { forwardRef, memo } from "react";
import type { Dispatch, SetStateAction } from "react";
import React, { useState, useRef } from "react";
import { v4 } from "uuid";

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";
import { Checkbox } from "../Checkbox";
import Dialog from "../Dialog";
import { IconButton } from "../theme";

export type TableProps = {
  className?: string;
  rows: object[];
  columnNames: string[];
  checkbox?: boolean;
  settings?: boolean;
  minWidth?: number | string;
  dialog?: { title: string; body: React.ReactNode; action: React.ReactNode };
  openDialog?: Dispatch<SetStateAction<object | null>>;
};

/**
 * A memoized functional component that renders a table.
 * @param {TableProps} props - The props object containing the necessary data for rendering the table.
 * @param {React.Ref<HTMLElement>} ref - The ref object for accessing the table element.
 * @returns The rendered table component.
 */
const Table = memo(
  forwardRef<HTMLElement, TableProps>((props) => {
    // Table Props
    const {
      // className,
      rows,
      columnNames,
      dialog,
      // checkbox,
      // settings,
      minWidth = 700,
      openDialog,
    } = props;

    // refs
    const dialogRef = useRef<HTMLDivElement>(null);

    // component state management
    const [dialogCoords] = useState<{ left: string; top: string } | null>(null);
    const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
    const [, setOpenedDialog] = useState<number | boolean>(false);
    const [iconButtonRefs] = useState<Array<React.RefObject<HTMLButtonElement>>>([]);
    IconButton;

    // related to styling
    const { classes } = useStyles(dialogCoords ? dialogCoords : { left: false, top: false });

    // Here we get the keys of the row so that we can render it
    type ObjectKeys = keyof (typeof rows)[0];
    const rowKeys: ObjectKeys[] = Object.keys(rows[0]) as ObjectKeys[];

    function openDialogInitializer(event: React.MouseEvent<HTMLButtonElement>, indx: number) {
      setAnchorEl(event.currentTarget);
      if (openDialog) {
        openDialog(rows[indx]);
      }
    }

    function closeTablePopover() {
      setAnchorEl(null);
      setOpenedDialog(false);
      if (openDialog) {
        openDialog(null);
      }
    }

    return (
      <TableContainer className={classes.tableContainer} component={Paper}>
        <MUITable sx={{ minWidth: minWidth }} aria-label="customized table">
          <TableHead>
            <TableRow>
              <TableCell className={classes.tableCell} />
              {columnNames.map((column) => (
                <TableCell className={classes.tableCell} key={column}>
                  {column}
                </TableCell>
              ))}
              <TableCell className={classes.tableCell} />
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row, indx) => (
              <TableRow className={classes.tableRow} key={v4()}>
                <TableCell className={classes.tableCell} padding="checkbox">
                  <Checkbox color="primary" defaultChecked />
                </TableCell>
                {/* { Object.keys(currObj).map((k)=>(

                ))} */}
                {rowKeys &&
                  rowKeys.map((key) => (
                    <TableCell className={classes.tableCell} component="th" scope="row" key={v4()}>
                      {row[key]}
                    </TableCell>
                  ))}

                <TableCell className={classes.tableCell} padding="none">
                  <IconButton
                    ref={iconButtonRefs[indx]}
                    onClick={(e) => openDialogInitializer(e, indx)}
                    iconId="moreVert"
                    // iconVariant="gray"
                    size="medium"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </MUITable>
        {anchorEl ? (
          <Dialog
            ref={dialogRef}
            anchorEl={anchorEl}
            onClick={closeTablePopover}
            title={dialog ? dialog.title : "unknown"}
            width="444px"
            direction="right"
            action={dialog?.action}>
            {dialog ? dialog.body : ""}
          </Dialog>
        ) : null}
      </TableContainer>
    );
  })
);

const useStyles = makeStyles<{ left: boolean | string; top: boolean | string }>({
  name: { Table },
})((theme, {}) => ({
  tableRow: {
    border: "none",
    backgroundColor: "transparent",
    "&:nth-of-type": {},
    "&:nth-of-type(odd)": {
      backgroundColor: changeColorOpacity({ color: theme.colors.palette.focus.main, opacity: 0.08 }),
      borderColor: changeColorOpacity({ color: theme.colors.palette.focus.main, opacity: 0.08 }),
    },
    // hide last border
    "&:last-child td, &:last-child th": {
      border: 0,
    },
  },
  tableCell: {
    [`&.${tableCellClasses.head}`]: {
      backgroundColor: "transparent",
      color: theme.colors.useCases.typography[theme.isDarkModeEnabled ? "textSecondary" : "textPrimary"],
      fontWeight: "bold",
      borderBottom: `0.5px solid ${
        theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1
      }`,
    },
    [`&.${tableCellClasses.body}`]: {
      fontSize: 14,
      border: "none",
    },
  },
  tableContainer: {
    boxShadow: "none",
    backgroundImage: "none",
    backgroundColor: "transparent",
  },
  tableCellText: {
    padding: theme.spacing(3),
    fontSize: "12px",
  },
}));

export default Table;
