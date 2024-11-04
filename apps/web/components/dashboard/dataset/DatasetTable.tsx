import { Box } from "@mui/material";
import { TablePagination } from "@mui/material";
import { useEffect, useState } from "react";

import { useDatasetCollectionItems } from "@/lib/api/layers";
import type { GetCollectionItemsQueryParams, Layer } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

import useLayerFields from "@/hooks/map/CommonHooks";

import DatasetTable from "@/components/common/DatasetTable";

interface DatasetTableTabProps {
  dataset: ProjectLayer | Layer;
}

const DatasetTableTab: React.FC<DatasetTableTabProps> = ({ dataset }) => {
  const { layerFields: fields, isLoading: areFieldsLoading } = useLayerFields(
    (dataset["id"] as string) || "",
    undefined
  );

  const [dataQueryParams, setDataQueryParams] = useState<GetCollectionItemsQueryParams>({
    limit: 25,
    offset: 0,
  });
  const { data } = useDatasetCollectionItems((dataset["id"] as string) || "", dataQueryParams);

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
    <Box>
      <Box
        sx={{
          height: `calc(100vh - 440px)`,
          overflowX: "hidden",
        }}>
        <DatasetTable areFieldsLoading={areFieldsLoading} displayData={displayData} fields={fields} />
      </Box>
      {displayData && (
        <TablePagination
          sx={{ mt: 2 }}
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={displayData.numberMatched}
          rowsPerPage={dataQueryParams.limit}
          page={dataQueryParams.offset ? dataQueryParams.offset / dataQueryParams.limit : 0}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      )}
    </Box>
  );
};

export default DatasetTableTab;
