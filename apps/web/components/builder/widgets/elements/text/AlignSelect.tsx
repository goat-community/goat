import type { Editor } from "@tiptap/react";
import { useTranslation } from "react-i18next";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import type { MenuItemOption } from "@/components/builder/widgets/elements/text/MenuSelect";
import { MenuSelect } from "@/components/builder/widgets/elements/text/MenuSelect";

const ALIGN_ITEMS: Array<Omit<MenuItemOption, "label"> & { labelKey: string }> = [
  { labelKey: "align_left", value: "left", icon: ICON_NAME.ALIGN_LEFT },
  { labelKey: "align_center", value: "center", icon: ICON_NAME.ALIGN_CENTER },
  { labelKey: "align_right", value: "right", icon: ICON_NAME.ALIGN_RIGHT },
  { labelKey: "justify", value: "justify", icon: ICON_NAME.ALIGN_JUSTIFY },
];

export const AlignSelect = ({
  editor,
  onOpen,
  onClose,
  forceClose,
}: {
  editor: Editor | null;
  onOpen?: () => void;
  onClose?: () => void;
  forceClose?: boolean;
}) => {
  const { t } = useTranslation("common");
  if (!editor) return null;

  const currentAlign =
    (editor.isActive({ textAlign: "center" }) && "center") ||
    (editor.isActive({ textAlign: "right" }) && "right") ||
    (editor.isActive({ textAlign: "justify" }) && "justify") ||
    "left";

  return (
    <MenuSelect
      buttonValue="textAlign"
      items={ALIGN_ITEMS.map(({ labelKey, ...item }) => ({ ...item, label: t(labelKey) }))}
      value={currentAlign}
      onOpen={onOpen}
      onClose={onClose}
      forceClose={forceClose}
      onChange={(val) => {
        editor.chain().focus().setTextAlign(val).run();
      }}
    />
  );
};
