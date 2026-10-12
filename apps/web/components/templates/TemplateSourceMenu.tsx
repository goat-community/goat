"use client";

import { useTranslation } from "react-i18next";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import { templateSourceOptions } from "@/lib/utils/templates";
import type { Space } from "@/lib/validations/content";
import type { TemplateSourceFilter } from "@/lib/validations/template";

import PillMenu from "@/components/dashboard/common/PillMenu";

interface TemplateSourceMenuProps {
  source: TemplateSourceFilter;
  onChange: (source: TemplateSourceFilter) => void;
  /** Which of Team/Organization to offer is read off the caller's spaces
   * (T7) — Everyone, GOAT and Mine are always available. */
  spaces: Space[];
  /** Phone layout: icon-only pill. */
  compact?: boolean;
}

/** The glyph each source is shown under, in the menu and on the pill once
 * it is the one in force. */
const SOURCE_ICON: Record<TemplateSourceFilter, ICON_NAME> = {
  all: ICON_NAME.GLOBE,
  goat: ICON_NAME.STAR,
  mine: ICON_NAME.USER,
  team: ICON_NAME.USERS,
  org: ICON_NAME.ORGANIZATION,
  shared: ICON_NAME.SHARE,
};

/** T7's template source on Home, as one tool pill with a menu: Everyone /
 * GOAT / Mine always, Team only once the caller is in a team space,
 * Organization only once an organization space exists, Shared with me once
 * either does — a personal-only account never sees a source it has nothing
 * behind. */
const TemplateSourceMenu = ({ source, onChange, spaces, compact }: TemplateSourceMenuProps) => {
  const { t } = useTranslation("common");
  const options = templateSourceOptions(spaces).map((option) => ({
    value: option.value,
    label: t(option.labelKey),
    icon: SOURCE_ICON[option.value],
  }));

  return (
    <PillMenu
      value={source}
      options={options}
      onChange={onChange}
      icon={SOURCE_ICON.all}
      active={source !== "all"}
      flat
      compact={compact}
      label={t("source")}
    />
  );
};

export default TemplateSourceMenu;
