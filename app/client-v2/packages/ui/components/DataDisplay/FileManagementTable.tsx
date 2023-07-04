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

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";
import { Text } from "../theme";
import { IconButton } from "../theme";

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

function getComparator<Key extends keyof any>(
  order: Order,
  orderBy: Key
): (a: { [key in Key]: number | string }, b: { [key in Key]: number | string }) => number {
  return order === "desc"
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

// Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
// stableSort() brings sort stability to non-modern browsers (notably IE11). If you
// only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
// with exampleArray.slice().sort(exampleComparator)
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

interface FileManagementHeadProps {
  numSelected: number;
  onRequestSort: (event: React.MouseEvent<unknown>, property: any) => void;
  order: Order;
  orderBy: string | number;
  rowCount: number;
  columns: {
    id: string;
    numeric: boolean;
    label: string;
  }[];
}

function FileManagementHead(props: FileManagementHeadProps) {
  const { order, orderBy, numSelected, rowCount, onRequestSort, columns } = props;
  const createSortHandler = (property: any) => (event: React.MouseEvent<unknown>) => {
    onRequestSort(event, property);
  };

  const { classes } = useStyles();

  return (
    <TableHead>
      <TableRow>
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

type FileManagementProps = {
  rows: { name: React.ReactNode; [key: string]: any }[];
  hover?: boolean;
  columnNames: {
    id: string;
    numeric: boolean;
    label: string;
  }[];
  openDialog?: React.Dispatch<React.SetStateAction<object | null>>;
  modal?: { body: React.ReactNode; action: React.ReactNode; header: React.ReactNode } | null;
  openModal?: React.Dispatch<React.SetStateAction<object | null>>;
  setDialogAnchor?: React.Dispatch<React.SetStateAction<HTMLButtonElement | null>>;
  more?: boolean;
};

export function FileManagementTable(props: FileManagementProps) {
  const {
    rows,
    columnNames,
    openModal,
    setDialogAnchor,
    modal,
    openDialog,
    more = true,
    hover = false,
    ...rest
  } = props;

  type ObjectKeys = keyof (typeof rows)[0];

  const rowKeys: ObjectKeys[] = Object.keys(rows[0]) as ObjectKeys[];

  const [order, setOrder] = React.useState<Order>("asc");
  const [orderBy, setOrderBy] = React.useState(rowKeys[0]);
  const [selected, setSelected] = React.useState<(string | number)[]>([]);
  const [modalStatus, setModalStatus] = React.useState<boolean>(false);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);
  const { classes } = useStyles();

  const handleRequestSort = (event: React.MouseEvent<unknown>, property: keyof ObjectKeys) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const isSelected = (name: string | number) => selected.indexOf(name) !== -1;

  function handleRowClick(row: { [x: string]: string | number; [x: number]: string | number }) {
    if (openModal && !React.isValidElement(row.name)) {
      openModal(row);
    } else {
    }
  }

  function openDialogInitializer(event: React.MouseEvent<HTMLButtonElement>, indx: number) {
    if (setDialogAnchor) {
      setDialogAnchor(event.currentTarget);
      if (openDialog) {
        openDialog(rows[indx]);
      }
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
                    {rowKeys &&
                      rowKeys.map((key, index) => (
                        <TableCell
                          onClick={() => handleRowClick(row)}
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
                          onClick={(e) => openDialogInitializer(e, index)}
                          iconId="moreVert"
                          size="medium"
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
    fontSize: "12px",
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
