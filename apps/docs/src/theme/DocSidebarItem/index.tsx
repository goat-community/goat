import type { PropSidebarItemCategory } from "@docusaurus/plugin-content-docs";
import { useVisibleSidebarItems } from "@docusaurus/plugin-content-docs/client";
import { ThemeClassNames } from "@docusaurus/theme-common";
import DocSidebarItem from "@theme-original/DocSidebarItem";
import type { Props } from "@theme/DocSidebarItem";
import DocSidebarItems from "@theme/DocSidebarItems";
import clsx from "clsx";
import React, { type ReactNode } from "react";

type SectionProps = Omit<Props, "item"> & { item: PropSidebarItemCategory };

/**
 * A top-level group of the docs sidebar (see `src/sidebar/sections.js`): a
 * small, non-interactive label with the group's pages always shown beneath.
 */
function DocSidebarSection({ item, onItemClick, activePath, level }: SectionProps): ReactNode {
  const items = useVisibleSidebarItems(item.items, activePath);
  return (
    <li
      className={clsx(
        ThemeClassNames.docs.docSidebarItemCategory,
        "menu__list-item",
        "sidebar-section",
        item.className
      )}>
      <div className="sidebar-section__label">{item.label}</div>
      <ul className="menu__list sidebar-section__items">
        <DocSidebarItems items={items} onItemClick={onItemClick} activePath={activePath} level={level + 1} />
      </ul>
    </li>
  );
}

export default function DocSidebarItemWrapper(props: Props): ReactNode {
  const { item } = props;
  if (item.type === "category" && item.customProps?.section) {
    return <DocSidebarSection {...props} item={item} />;
  }
  return <DocSidebarItem {...props} />;
}
