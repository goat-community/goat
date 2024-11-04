import { IconButton } from "@mui/material";
import { Dialog, DialogActions, DialogContent, DialogTitle, Stack, TablePagination } from "@mui/material";
import { useEffect, useState } from "react";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useDatasetCollectionItems } from "@/lib/api/layers";
import type { GetCollectionItemsQueryParams, Layer } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

import useLayerFields from "@/hooks/map/CommonHooks";

import DatasetTable from "@/components/common/DatasetTable";

interface DatasetTableDialogProps {
  open: boolean;
  onClose?: () => void;
  disabled?: boolean;
  dataset: ProjectLayer | Layer;
}

const DatasetTableModal: React.FC<DatasetTableDialogProps> = ({ open, onClose, dataset }) => {
  const { layerFields: fields, isLoading: areFieldsLoading } = useLayerFields(
    dataset["layer_id"] || dataset["id"] || "",
    undefined
  );
  const defaultParams = {
    limit: 50,
    offset: 0,
  };
  if (dataset["query"]?.["cql"]) {
    defaultParams["filter"] = JSON.stringify(dataset["query"]["cql"]);
  }
  const [dataQueryParams, setDataQueryParams] = useState<GetCollectionItemsQueryParams>(defaultParams);
  const { data } = useDatasetCollectionItems(dataset["layer_id"] || dataset["id"] || "", dataQueryParams);

  const [displayData, setDisplayData] = useState(data);
  useEffect(() => {
    if (data) {
      setDisplayData(data);
    }
  }, [data]);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setDataQueryParams((prev) => ({
      ...prev,
      offset: newPage * prev.limit,
    }));
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDataQueryParams({
      limit: parseInt(event.target.value, 10),
      offset: 0,
    });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="lg">
      <DialogTitle>
        <Stack direction="row" spacing={1} justifyContent="space-between">
          {`${dataset.name}`}
          <IconButton onClick={() => onClose && onClose()}>
            <Icon iconName={ICON_NAME.CLOSE} htmlColor="inherit" fontSize="small" />
          </IconButton>
        </Stack>
      </DialogTitle>
      <DialogContent sx={{ px: 0, mx: 0, pb: 0, minHeight: "250px" }}>
        <DatasetTable areFieldsLoading={areFieldsLoading} displayData={displayData} fields={fields} />
      </DialogContent>
      <DialogActions sx={{ pb: 0 }}>
        {displayData && (
          <TablePagination
            rowsPerPageOptions={[10, 25, 50]}
            component="div"
            count={displayData.numberMatched}
            rowsPerPage={dataQueryParams.limit}
            page={dataQueryParams.offset ? dataQueryParams.offset / dataQueryParams.limit : 0}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DatasetTableModal;
