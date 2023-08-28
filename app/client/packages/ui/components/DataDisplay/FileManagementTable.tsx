"use client";

import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import { visuallyHidden } from "@mui/utils";
import * as React from "react";
import { isValidElement, useEffect } from "react";

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";
import { Icon, IconButton, Text } from "../theme";

// SORTING FUNCTIONS

/**
 * A comparator function used for sorting an array of objects in descending order based on a specific property.
 * @param {T} a - The first object to compare.
 * @param {T} b - The second object to compare.
 * @param {keyof T} orderBy - The property of the objects to sort by.
 * @returns {number} - Returns -1 if b[orderBy] is less than a[orderBy], 1 if b[orderBy] is greater than a[orderBy], or 0 if they are equal.
 */

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

type Order = "asc" | "desc";

/**
 * Returns a comparator function based on the given order and orderBy parameters.
 * @param {Order} order - The order in which to sort the items (asc or desc).
 * @param {Key} orderBy - The key to sort the items by.
 * @returns A comparator function that can be used to sort an array of objects.
 */

function getComparator(
  order,
  orderBy
){
  return order === "desc"
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

/**
 * Sorts an array in a stable manner using a custom comparator function.
 * @param {readonly T[]} array - The array to be sorted.
 * @param {(a: T, b: T) => number} comparator - The function used to compare elements in the array.
 * @returns {T[]} - The sorted array.
 */

function stableSort(array, comparator) {
  const stabilizedThis = array.map((el, index) => [el, index]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

interface FileManagementHeadProps {
  numSelected: number;
  onRequestSort: (event: React.MouseEvent<unknown>, property: any) => void;
  order: Order;
  orderBy: string | null | number;
  rowCount: number;
  columns: {
    id: string;
    numeric: boolean;
    label: string;
    isSortable?: boolean;
    icon?: any;
  }[];
}

/**
 * Renders the table head component for an enhanced table.
 * @param {EnhancedTableProps} props - The props for the EnhancedTableHead component.
 * @returns The rendered table head component.
 */

function FileManagementHead(props: FileManagementHeadProps) {
  const { order, orderBy, numSelected, rowCount, onRequestSort, columns } = props;
  const createSortHandler = (property: any) => (event: React.MouseEvent<unknown>) => {
    onRequestSort(event, property);
  };

  const { classes } = useStyles();

  console.log('numSelected', numSelected)
  console.log('rowCount', rowCount)

  return (
    <TableHead>
      <TableRow>
        {columns.map((headCell) => {
          if (headCell.isSortable) {
            return (
              <TableCell
                className={classes.tableCell}
                key={headCell.id}
                align={headCell.numeric ? "right" : "left"}
                sortDirection={orderBy === headCell.id ? order : false}>
                <TableSortLabel
                  active={orderBy === headCell.id}
                  direction={orderBy === headCell.id ? order : "asc"}
                  onClick={createSortHandler(headCell.id)}>
                  <Text className={classes.tableCellHeaderText} typo="body 1">
                    {headCell.label}
                  </Text>
                  {orderBy === headCell.id ? (
                    <Box component="span" sx={visuallyHidden}>
                      {order === "desc" ? "sorted descending" : "sorted ascending"}
                    </Box>
                  ) : null}
                </TableSortLabel>
              </TableCell>
            );
          } else {
            return (
              <TableCell
                className={classes.tableCell}
                key={headCell.id}
                align={headCell.numeric ? "right" : "left"}>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  {headCell.icon ? (
                    <Box component={headCell.icon} color="inherit" sx={{ mr: 1, color: "#2BB381" }} />
                  ) : null}
                  <Text className={classes.tableCellHeaderText} typo="body 1">
                    {headCell.label}
                  </Text>
                </Box>
              </TableCell>
            );
          }
        })}
        <TableCell className={classes.tableCell} padding="checkbox" />
      </TableRow>
    </TableHead>
  );
}

type Rows = { name: React.ReactNode; [key: string]: any };

type FileManagementProps = {
  rows: Rows[];
  hover?: boolean;
  columnNames: {
    id: string;
    numeric: boolean;
    label: string;
  }[];
  setDialogContent?: React.Dispatch<
    React.SetStateAction<{
      name: React.ReactNode;
      type: React.ReactNode;
      modified: string;
      size: string;
    } | null>
  >;
  modal?: { body: React.ReactNode; action: React.ReactNode; header: React.ReactNode } | null;
  setModalContent?: React.Dispatch<React.SetStateAction<object | null>>;
  setDialogAnchor?: React.Dispatch<React.SetStateAction<HTMLButtonElement | null>>;
  more?: boolean;
  currPath: string[];
  setPath: (value: string[]) => void;
};

/**
 * Renders an enhanced table component with customizable props.
 * @param {EnhanceTableProps} props - The props object containing the necessary data for rendering the table.
 * @returns The rendered enhanced table component.
 */

export function FileManagementTable(props: FileManagementProps) {
  const {
    rows,
    columnNames,
    setModalContent,
    setDialogAnchor,
    setDialogContent,
    more = true,
    hover = false,
    currPath,
    setPath,
  } = props;

  const { classes } = useStyles();

  // Component State
  const [order, setOrder] = React.useState<Order>("asc");
  const [orderBy, setOrderBy] = React.useState<string | null>(null);
  const [selected] = React.useState<(string | number)[]>([]);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(25);
  const [rowOnPath, setRowOnPath] = React.useState<Rows[] | null>(rows);

  useEffect(() => {
    switchPath({
      direction: "change",
      changePath: currPath,
    });
  }, [currPath]);

  // functions
  const handleRequestSort = (_: React.MouseEvent<unknown>, property: any) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  /**
   * Recursively searches for an element in an array of objects with nested paths.
   * @param {Rows[]} rows - The array of objects to search through.
   * @param {string[]} targetPath - The target path to search for.
   * @returns {Rows[] | null} - An array of objects that match the target path, or null if no match is found.
   */
  function findElementWithNestedPath(rows: Rows[], targetPath: string[]) {
    let files: Rows[] = [];

    rows.map((row) => {
      if (JSON.stringify(row.path) === JSON.stringify(targetPath)) {
        files.push(row);
      }
      if (row.files) {
        const nestedResult = findElementWithNestedPath(row.files, targetPath);
        if (nestedResult) {
          files = [...files, ...nestedResult];
        }
      }
    });

    if (files.length) {
      return files;
    }
    return null;
  }

  function findSiblingsWithNestedPath(rows: Rows[], targetPath: string[]) {
    const targetElement = findElementWithNestedPath(rows, targetPath);
    if (!targetElement) {
      return [];
    }
    return targetElement;
  }

  function switchPath(props: {
    direction: "back" | "enter" | "change";
    currPath?: string[];
    changePath?: string[];
    folderName?: string;
  }) {
    let newPath: string[] = [];

    switch (props.direction) {
      case "back":
        if (props.currPath) {
          newPath = [...props.currPath];
          newPath.pop();
          setPath(newPath);
          break;
        }
      case "enter":
        if (props.folderName && props.currPath) {
          newPath = [...props.currPath];
          newPath.push(props.folderName);
          setPath(newPath);
        }
        break;
      case "change":
        if (props.changePath) {
          newPath = props.changePath;
          setPath(newPath);
        }
        break;
    }

    if (newPath.length) {
      const siblings = findSiblingsWithNestedPath(rows, newPath);
      setRowOnPath(siblings.flat(Infinity));
    }
  }

  function handleRowClick(row) {
    if (setModalContent && !React.isValidElement(row.name) && row.name !== "...") {
      setModalContent(row);
    } else {
      if (row.files) {
        switchPath({
          direction: "enter",
          currPath: row.path,
          folderName: row.stringName,
        });
      } else if (row.name === "..." && currPath.length > 1) {
        switchPath({
          direction: "back",
          currPath: currPath,
        });
      }
    }
  }

  function openDialogInitializer(
    event: React.MouseEvent<HTMLButtonElement>,
    row: {
      name: React.ReactNode;
      type: React.ReactNode;
      modified: string;
      size: string;
    }
  ) {
    if (setDialogAnchor) {
      setDialogAnchor(event.currentTarget);
      if (setDialogContent) {
        setDialogContent(row);
      }
    }
  }

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

  const visibleRows = React.useMemo(() => {
    return stableSort(rowOnPath ? rowOnPath : [], getComparator(order, orderBy)).slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    );
  }, [order, orderBy, page, rowsPerPage, rowOnPath]);

  useEffect(() => {
    setRowOnPath(rows);

    if (rows.length) {
      // Here we get the keys of the row so that we can render it

      const rowKeys = Object.keys(rows[0])
      setOrderBy(rowKeys[0]);
    }
  }, [rows.length]);

  if (!rows?.length) {
    return <div>No Items</div>;
  }

  return (
    <Box sx={{ width: "100%" }}>
      <Paper sx={{ width: "100%", mb: 2 }} className={classes.tableContainer}>
        <TableContainer>
          <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size="small">
            <FileManagementHead
              numSelected={selected.length}
              order={order}
              columns={columnNames}
              orderBy={orderBy}
              onRequestSort={handleRequestSort}
              rowCount={rows.length}
            />
            <TableBody>
              <TableRow
                className={classes.tableRow}
                onClick={() => handleRowClick({ name: "..." })}
                hover={hover}
                role="checkbox"
                tabIndex={-1}
                sx={{ cursor: "pointer" }}>
                <TableCell
                  className={classes.tableCell}
                  sx={{ padding: "12px" }}
                  component="th"
                  id="go-back"
                  scope="row"
                  padding="none">
                  <Text className={classes.tableCellText} typo="body 2">
                    <Icon iconId="moreHorizontal" iconVariant="gray" />
                  </Text>
                </TableCell>
                <TableCell
                  className={classes.tableCell}
                  component="th"
                  id="go-back"
                  scope="row"
                  padding="none"
                />
                <TableCell
                  className={classes.tableCell}
                  component="th"
                  id="go-back"
                  scope="row"
                  padding="none"
                />
                <TableCell
                  className={classes.tableCell}
                  component="th"
                  id="go-back"
                  scope="row"
                  padding="none"
                />
                <TableCell
                  className={classes.tableCell}
                  component="th"
                  id="go-back"
                  scope="row"
                  padding="none"
                />
              </TableRow>
              {visibleRows.map((row, index) => {
                const labelId = `enhanced-table-checkbox-${index}`;

                return (
                  <TableRow
                    className={classes.tableRow}
                    hover={hover}
                    role="checkbox"
                    tabIndex={-1}
                    key={index}
                    sx={{ cursor: "pointer" }}>
                    <TableCell
                      onClick={() => handleRowClick(row)}
                      className={classes.tableCell}
                      component="th"
                      id={labelId}
                      scope="row"
                      padding="none">
                      {isValidElement(row.name) ? (
                        row.name
                      ) : (
                        <Text className={classes.tableCellText} typo="body 2">
                          {row.name}
                        </Text>
                      )}
                    </TableCell>
                    <TableCell
                      onClick={() => handleRowClick(row)}
                      className={classes.tableCell}
                      component="th"
                      id={labelId}
                      scope="row"
                      padding="none">
                      {row.chip}
                    </TableCell>
                    <TableCell
                      onClick={() => handleRowClick(row)}
                      className={classes.tableCell}
                      component="th"
                      id={labelId}
                      scope="row"
                      padding="none">
                      <Text className={classes.tableCellText} typo="body 2">
                        {row.modified}
                      </Text>
                    </TableCell>
                    <TableCell
                      onClick={() => handleRowClick(row)}
                      className={classes.tableCell}
                      component="th"
                      id={labelId}
                      scope="row"
                      padding="none">
                      <Text className={classes.tableCellText} typo="body 2">
                        {row.size}
                      </Text>
                    </TableCell>
                    {more ? (
                      <TableCell className={classes.tableCell} padding="none">
                        <IconButton
                          onClick={(e) => openDialogInitializer(e, row)}
                          iconId="moreVert"
                          size="large"
                        />
                      </TableCell>
                    ) : null}
                  </TableRow>
                );
              })}
              {emptyRows > 0 && (
                <TableRow
                  style={{
                    height: 33 * emptyRows,
                  }}>
                  <TableCell colSpan={6} />
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={rows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
}

const useStyles = makeStyles({
  name: { FileManagementTable },
})((theme) => ({
  tableRow: {
    backgroundColor: "transparent",
    "&:nth-of-type": {},
    "&:nth-of-type(odd)": {
      backgroundColor: "transparent",
      borderColor: changeColorOpacity({ color: theme.colors.palette.focus.main, opacity: 0.08 }),
    },
    "&.MuiTableRow-hover:hover": {
      background: `${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}80`,
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
      borderBottom: `0.5px solid ${
        theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1
      }`,
    },
    paddingLeft: theme.spacing(3),
  },
  tableContainer: {
    boxShadow: "none",
    backgroundImage: "none",
    backgroundColor: "transparent",
  },
  tableCellText: {
    padding: 0,
  },
  tableCellHeaderText: {
    fontWeight: "bold",
    paddingLeft: 0,
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
}));
