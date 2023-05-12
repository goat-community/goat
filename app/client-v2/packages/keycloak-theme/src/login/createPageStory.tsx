import type { DeepPartial } from "keycloakify/tools/DeepPartial";

import KcApp from "./KcApp";
import { getKcContext, type KcContext } from "./kcContext";

export function createPageStory<PageId extends KcContext["pageId"]>(params: { pageId: PageId }) {
  const { pageId } = params;

  function PageStory(params: { kcContext?: DeepPartial<Extract<KcContext, { pageId: PageId }>> }) {
    const { kcContext } = getKcContext({
      mockPageId: pageId,
      storyPartialKcContext: params.kcContext,
    });

    return <KcApp kcContext={kcContext} />;
  }

  return { PageStory };
}
