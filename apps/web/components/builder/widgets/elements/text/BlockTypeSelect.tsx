import type { Editor } from "@tiptap/react";
import { useEditorState } from "@tiptap/react";
import { useTranslation } from "react-i18next";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import type { MenuItemOption } from "@/components/builder/widgets/elements/text/MenuSelect";
import { MenuSelect } from "@/components/builder/widgets/elements/text/MenuSelect";

const BLOCK_TYPE_ITEMS: Array<Omit<MenuItemOption, "label"> & { labelKey: string }> = [
  { labelKey: "text", value: "paragraph", icon: ICON_NAME.TEXT },
  { labelKey: "heading_1", value: "heading1", icon: ICON_NAME.H1 },
  { labelKey: "heading_2", value: "heading2", icon: ICON_NAME.H2 },
  { labelKey: "heading_3", value: "heading3", icon: ICON_NAME.H3 },
  { labelKey: "bulleted_list", value: "bulletList", icon: ICON_NAME.BULLET_LIST },
  { labelKey: "numbered_list", value: "orderedList", icon: ICON_NAME.NUMBERED_LIST },
  { labelKey: "code_block", value: "codeBlock", icon: ICON_NAME.CODE },
];

const getCurrentBlock = (editor: Editor) => {
  if (editor.isActive("bulletList")) return "bulletList";
  if (editor.isActive("orderedList")) return "orderedList";
  if (editor.isActive("codeBlock")) return "codeBlock";
  if (editor.isActive("paragraph")) return "paragraph";
  if (editor.isActive("heading", { level: 1 })) return "heading1";
  if (editor.isActive("heading", { level: 2 })) return "heading2";
  if (editor.isActive("heading", { level: 3 })) return "heading3";
  return "paragraph";
};

export const BlockTypeSelect = ({
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
  const editorState = useEditorState({
    editor,
    selector: (snapshot) => {
      const e = snapshot.editor;
      return { currentBlock: e ? getCurrentBlock(e) : "paragraph" };
    },
  });

  if (!editor) return null;

  return (
    <MenuSelect
      buttonValue="blockType"
      items={BLOCK_TYPE_ITEMS.map(({ labelKey, ...item }) => ({ ...item, label: t(labelKey) }))}
      value={editorState?.currentBlock ?? "paragraph"}
      onOpen={onOpen}
      onClose={onClose}
      forceClose={forceClose}
      onChange={(val) => {
        switch (val) {
          case "bulletList":
            editor.chain().focus().toggleBulletList().run();
            break;
          case "orderedList":
            editor.chain().focus().toggleOrderedList().run();
            break;
          case "codeBlock":
            editor.chain().focus().toggleCodeBlock().run();
            break;
          case "paragraph":
            editor.chain().focus().setParagraph().run();
            break;
          case "heading1":
            editor.chain().focus().toggleHeading({ level: 1 }).run();
            break;
          case "heading2":
            editor.chain().focus().toggleHeading({ level: 2 }).run();
            break;
          case "heading3":
            editor.chain().focus().toggleHeading({ level: 3 }).run();
            break;
        }
      }}
    />
  );
};
