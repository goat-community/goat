import { translate } from "@docusaurus/Translate";
import { useDoc } from "@docusaurus/plugin-content-docs/client";
import { useWindowSize } from "@docusaurus/theme-common";
import CopyPageButton from "@site/src/components/CopyPageButton";
import DocFeedback from "@site/src/components/DocFeedback";
import ContentVisibility from "@theme/ContentVisibility";
import DocBreadcrumbs from "@theme/DocBreadcrumbs";
import DocItemContent from "@theme/DocItem/Content";
import DocItemFooter from "@theme/DocItem/Footer";
import type { Props } from "@theme/DocItem/Layout";
import DocItemPaginator from "@theme/DocItem/Paginator";
import DocItemTOCDesktop from "@theme/DocItem/TOC/Desktop";
import DocItemTOCMobile from "@theme/DocItem/TOC/Mobile";
import DocVersionBadge from "@theme/DocVersionBadge";
import DocVersionBanner from "@theme/DocVersionBanner";
import clsx from "clsx";
import React, { type ReactNode } from "react";

import styles from "./styles.module.css";

/**
 * The right-hand column ("On this page" and the feedback widget) is shown on
 * desktop viewports unless the doc hides its table of contents. Elsewhere the
 * feedback widget moves below the content.
 */
function useDocAside() {
  const { frontMatter, toc } = useDoc();
  const windowSize = useWindowSize();

  const hidden = Boolean(frontMatter.hide_table_of_contents);
  const hasToc = !hidden && toc.length > 0;
  const isDesktop = windowSize === "desktop" || windowSize === "ssr";

  return {
    hidden,
    hasToc,
    showAside: !hidden && isDesktop,
  };
}

export default function DocItemLayout({ children }: Props): ReactNode {
  const { metadata } = useDoc();
  const { hidden, hasToc, showAside } = useDocAside();

  return (
    <div className="row">
      <div className={clsx("col", !hidden && styles.docItemCol)}>
        <ContentVisibility metadata={metadata} />
        <DocVersionBanner />
        <div className={styles.docItemContainer}>
          <article>
            <div className={styles.docHeader}>
              <div className={styles.docHeaderBreadcrumbs}>
                <DocBreadcrumbs />
              </div>
              <CopyPageButton className={styles.docHeaderAction} />
            </div>
            <DocVersionBadge />
            {hasToc && <DocItemTOCMobile />}
            <DocItemContent>{children}</DocItemContent>
            {!showAside && <DocFeedback className={styles.feedbackBottom} />}
            <DocItemFooter />
          </article>
          <DocItemPaginator />
        </div>
      </div>
      {showAside && (
        <div className="col col--3">
          <aside className={styles.aside}>
            {hasToc && (
              <>
                <div className={styles.asideTitle}>
                  {translate({
                    id: "theme.TOCCollapsible.toggleButtonLabel",
                    message: "On this page",
                    description: "The label used by the button on the collapsible TOC component",
                  })}
                </div>
                <DocItemTOCDesktop />
              </>
            )}
            <DocFeedback className={styles.feedbackAside} />
          </aside>
        </div>
      )}
    </div>
  );
}
