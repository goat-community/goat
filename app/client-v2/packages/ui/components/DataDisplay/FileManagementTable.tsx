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
import { isValidElement, useEffect } from "react";
import * as React from "react";

import { changeColorOpacity } from "../../lib";
import { makeStyles } from "../../lib/ThemeProvider";
import { Text, Icon, IconButton } from "../theme";

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
function stableSort<T extends Rows>(array: readonly T[], comparator: (a: T, b: T) => number) {
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

type Rows = { name: React.ReactNode; [key: string]: any };

type FileManagementProps = {
  rows: Rows[];
  hover?: boolean;
  columnNames: {
    id: string;
    numeric: boolean;
    label: string;
  }[];
  openDialog?: React.Dispatch<
    React.SetStateAction<{
      [x: string]: string | number;
      [x: number]: string | number;
    } | null>
  >;
  modal?: { body: React.ReactNode; action: React.ReactNode; header: React.ReactNode } | null;
  openModal?: React.Dispatch<React.SetStateAction<object | null>>;
  setDialogAnchor?: React.Dispatch<React.SetStateAction<HTMLButtonElement | null>>;
  more?: boolean;
  currPath: string[];
  setPath: (value: string[]) => void;
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
    currPath,
    setPath,
    ...rest
  } = props;

  type ObjectKeys = keyof (typeof rows)[0];

  const rowKeys: ObjectKeys[] = Object.keys(rows[0]) as ObjectKeys[];

  const [order, setOrder] = React.useState<Order>("asc");
  const [orderBy, setOrderBy] = React.useState(rowKeys[0]);
  const [selected, setSelected] = React.useState<(string | number)[]>([]);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(20);
  const [rowOnPath, setRowOnPath] = React.useState<Rows[] | null>(rows);
  const { classes } = useStyles();

  useEffect(() => {
    switchPath({
      direction: "change",
      changePath: currPath,
    });
  }, [currPath]);

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

  function handleRowClick(row: Rows) {
    if (openModal && !React.isValidElement(row.name) && row.name !== "...") {
      openModal(row);
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
    row: { [x: string]: string | number; [x: number]: string | number }
  ) {
    if (setDialogAnchor) {
      setDialogAnchor(event.currentTarget);
      if (openDialog) {
        openDialog(row);
      }
    }
  }

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

  const visibleRows: Rows[] = React.useMemo(() => {
    const stable_sort = stableSort(rowOnPath ? rowOnPath : [], getComparator(order, orderBy)).slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    );
    return stable_sort;
  }, [order, orderBy, page, rowsPerPage, rowOnPath]);

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
                      {row.type}
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
