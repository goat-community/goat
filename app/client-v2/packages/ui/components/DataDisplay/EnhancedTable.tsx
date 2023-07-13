import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
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

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";
import Dialog from "../Dialog";
import { Text } from "../theme";
import { IconButton } from "../theme";

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

function getComparator<Key extends keyof any>(
  order: Order,
  orderBy: Key
): (a: { [key in Key]: number | string }, b: { [key in Key]: number | string }) => number {
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

function stableSort<T>(array: readonly T[], comparator: (a: T, b: T) => number) {
  const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

interface EnhancedTableProps {
  numSelected: number;
  onRequestSort: (event: React.MouseEvent<unknown>, property: any) => void;
  onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
  order: Order;
  orderBy: string | number;
  rowCount: number;
  columns: {
    id: string;
    numeric: boolean;
    label: string;
  }[];
  checkbox: boolean;
}

/**
 * Renders the table head component for an enhanced table.
 * @param {EnhancedTableProps} props - The props for the EnhancedTableHead component.
 * @returns The rendered table head component.
 */
function EnhancedTableHead(props: EnhancedTableProps) {
  const { onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort, columns, checkbox } = props;

  const { classes } = useStyles({ dense: undefined, alternativeColors: false, checkbox });

  // functions

  const createSortHandler = (property: any) => (event: React.MouseEvent<unknown>) => {
    onRequestSort(event, property);
  };

  return (
    <TableHead>
      <TableRow>
        {checkbox ? (
          <TableCell className={classes.tableCell} padding="checkbox">
            <Checkbox
              color="primary"
              indeterminate={numSelected > 0 && numSelected < rowCount}
              checked={rowCount > 0 && numSelected === rowCount}
              onChange={onSelectAllClick}
              inputProps={{
                "aria-label": "select all desserts",
              }}
            />
          </TableCell>
        ) : null}
        {columns.map((headCell) => (
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
        ))}
        <TableCell className={classes.tableCell} padding="checkbox" />
      </TableRow>
    </TableHead>
  );
}

type EnhanceTableProps = {
  rows: { name: React.ReactNode; [key: string]: any }[];
  dense: boolean;
  alternativeColors: boolean;
  hover?: boolean;
  columnNames: {
    id: string;
    numeric: boolean;
    label: string;
  }[];
  openDialog?: React.Dispatch<React.SetStateAction<object | null>>;
  dialog?: { title: string; body: React.ReactNode; action: React.ReactNode };
  checkbox?: boolean;
  more?: boolean;
};

/**
 * Renders an enhanced table component with customizable props.
 * @param {EnhanceTableProps} props - The props object containing the necessary data for rendering the table.
 * @returns The rendered enhanced table component.
 */
export function EnhancedTable(props: EnhanceTableProps) {
  const {
    rows,
    columnNames,
    openDialog,
    dense,
    dialog,
    checkbox = true,
    more = true,
    alternativeColors = true,
    hover = false,
    ...rest
  } = props;

  const { classes } = useStyles({ dense, alternativeColors, checkbox });

  // Here we get the keys of the row so that we can render it
  type ObjectKeys = keyof (typeof rows)[0];
  const rowKeys: ObjectKeys[] = Object.keys(rows[0]) as ObjectKeys[];

  // Component State
  const [order, setOrder] = React.useState<Order>("asc");
  const [orderBy, setOrderBy] = React.useState(rowKeys[0]);
  const [selected, setSelected] = React.useState<(string | number)[]>([]);
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(25);

  // functions
  const handleRequestSort = (event: React.MouseEvent<unknown>, property: keyof ObjectKeys) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = rows.map((n) => n.name);
      setSelected(newSelected);
      return;
    }
    setSelected([]);
  };

  const handleClick = (event: React.MouseEvent<unknown>, name: string | number) => {
    const selectedIndex = selected.indexOf(name);
    let newSelected: readonly string[] = [];
    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
    }

    setSelected(newSelected);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const isSelected = (name: string | number) => selected.indexOf(name) !== -1;

  function openDialogInitializer(
    event: React.MouseEvent<HTMLButtonElement>,
    row: { [x: string]: string | number; [x: number]: string | number }
  ) {
    setAnchorEl(event.currentTarget);
    if (openDialog) {
      openDialog(row);
    }
  }

  function closeTablePopover() {
    setAnchorEl(null);
    if (openDialog) {
      openDialog(null);
    }
  }

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

  const visibleRows = React.useMemo(
    () =>
      stableSort(rows, getComparator(order, orderBy)).slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
      ),
    [order, orderBy, page, rowsPerPage]
  );

  return (
    <Box sx={{ width: "100%" }}>
      <Paper sx={{ width: "100%", mb: 2 }} className={classes.tableContainer}>
        <TableContainer>
          <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size={dense ? "small" : "medium"}>
            <EnhancedTableHead
              numSelected={selected.length}
              order={order}
              columns={columnNames}
              orderBy={orderBy}
              onSelectAllClick={handleSelectAllClick}
              onRequestSort={handleRequestSort}
              rowCount={rows.length}
              checkbox={checkbox}
            />
            <TableBody>
              {visibleRows.map((row, index) => {
                const isItemSelected = isSelected(row.name);
                const labelId = `enhanced-table-checkbox-${index}`;

                return (
                  <TableRow
                    className={classes.tableRow}
                    hover={hover}
                    role="checkbox"
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={index}
                    selected={isItemSelected}
                    sx={{ cursor: "pointer" }}>
                    {checkbox ? (
                      <TableCell className={classes.tableCell} padding="checkbox">
                        <Checkbox
                          color="primary"
                          onClick={(event) => handleClick(event, row.name)}
                          checked={isItemSelected}
                          inputProps={{
                            "aria-labelledby": labelId,
                          }}
                        />
                      </TableCell>
                    ) : null}
                    {rowKeys &&
                      rowKeys.map((key, index) => (
                        <TableCell
                          className={classes.tableCell}
                          key={index}
                          component="th"
                          id={labelId}
                          scope="row"
                          padding="none">
                          <Text className={classes.tableCellText} typo="body 2">
                            {row[key]}
                          </Text>
                        </TableCell>
                      ))}
                    {more ? (
                      <TableCell className={classes.tableCell} padding="none">
                        <IconButton
                          onClick={(e) => openDialogInitializer(e, row)}
                          iconId="moreVert"
                          // iconVariant="gray"
                          size="medium"
                        />
                      </TableCell>
                    ) : null}
                    {/* <TableCell align="right">{row.calories}</TableCell>
                    <TableCell align="right">{row.fat}</TableCell>
                    <TableCell align="right">{row.carbs}</TableCell>
                    <TableCell align="right">{row.protein}</TableCell> */}
                  </TableRow>
                );
              })}
              {emptyRows > 0 && (
                <TableRow
                  style={{
                    height: (dense ? 33 : 53) * emptyRows,
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
      {anchorEl ? (
        <Dialog
          anchorEl={anchorEl}
          onClick={closeTablePopover}
          title={dialog ? dialog.title : "unknown"}
          width="523px"
          direction="right"
          action={dialog?.action}>
          {dialog ? dialog.body : ""}
        </Dialog>
      ) : null}
    </Box>
  );
}

const useStyles = makeStyles<{ dense?: boolean | undefined; alternativeColors: boolean; checkbox: boolean }>({
  name: { EnhancedTable },
})((theme, { dense, alternativeColors, checkbox }) => ({
  tableRow: {
    backgroundColor: "transparent",
    "&:nth-of-type": {},
    "&:nth-of-type(odd)": {
      backgroundColor: alternativeColors
        ? changeColorOpacity({ color: theme.colors.palette.focus.main, opacity: 0.08 })
        : "transparent",
      borderColor: changeColorOpacity({ color: theme.colors.palette.focus.main, opacity: 0.08 }),
    },
    // hide last border
    "&:last-child td, &:last-child th": {
      border: alternativeColors ? 0 : "",
    },
    "&.MuiTableRow-hover:hover": {
      background: theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1,
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
      borderBottom: alternativeColors
        ? "none"
        : `0.5px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}`,
    },
    paddingLeft: checkbox ? 0 : theme.spacing(3),
  },
  tableContainer: {
    boxShadow: "none",
    backgroundImage: "none",
    backgroundColor: "transparent",
  },
  tableCellText: {
    padding: dense ? 0 : theme.spacing(3),
    fontSize: "12px",
  },
  tableCellHeaderText: {
    fontWeight: "bold",
    paddingLeft: checkbox ? theme.spacing(3) : 0,
  },
}));
