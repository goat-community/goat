import { Alert } from "@mui/material";
import { Stack } from "@mui/material";

import { Loading } from "@p4b/ui/components/Loading";

import { useTranslation } from "@/i18n/client";

interface ChartStatusContainerProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  queryParams?: any;
  isLoading: boolean;
  isError: boolean;
  height?: number | string;
  customStates?: Array<{
    condition: boolean;
    element: React.ReactNode;
  }>;
  infoMessage?: string;
  errorMessage?: string;
}

export const ChartStatusContainer = ({
  config,
  queryParams,
  isLoading,
  isError,
  height = 200,
  customStates = [],
  infoMessage,
  errorMessage,
}: ChartStatusContainerProps) => {
  const { t } = useTranslation("common");

  // Default states that apply to all charts
  const defaultStates = [
    {
      condition: !!config && !!queryParams && isLoading,
      element: <Loading />,
    },
    {
      condition: !!config && !queryParams,
      element: <Alert severity="info">{infoMessage ?? t("please_configure_chart")}</Alert>,
    },
    {
      condition: !config || isError,
      element: <Alert severity="error">{errorMessage ?? t("cannot_render_chart_error")}</Alert>,
    },
    ...customStates, // Add any custom states passed by the component
  ];

  const content = defaultStates.find((state) => state.condition)?.element;

  if (!content) {
    return null;
  }

  return (
    <Stack alignItems="center" justifyContent="center" width="100%" height={height}>
      {content}
    </Stack>
  );
};
