import { ICON_NAME } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import { setActiveLeftPanel } from "@/lib/store/map/slice";

import { useAppDispatch } from "@/hooks/store/ContextHooks";

import EmptySection from "@/components/common/EmptySection";
import Container from "@/components/map/panels/Container";

const ChartsPanel = () => {
  const dispatch = useAppDispatch();
  const { t } = useTranslation("common");
  return (
    <Container
      close={() => dispatch(setActiveLeftPanel(undefined))}
      title={t("charts")}
      direction="left"
      body={<EmptySection label={t("coming_soon")} icon={ICON_NAME.COMING_SOON} />}
    />
  );
};

export default ChartsPanel;
