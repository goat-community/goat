import { Box, Button, Stack, styled } from "@mui/material";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

import type { TextElementSchema } from "@/lib/validations/widget";

import { ArrowPopper } from "@/components/ArrowPoper";

export const TipTapEditorContent = styled(EditorContent)(({ theme }) => ({
  flexGrow: 1,
  height: "100%",
  padding: theme.spacing(1),
  overflowY: "auto",
  "& > .ProseMirror-focused": {
    outline: `1px solid ${theme.palette.primary.main}`,
    borderRadius: theme.shape.borderRadius,
  },
  "& > .ProseMirror:focus": {
    outline: `1px solid ${theme.palette.primary.main}`,
    borderRadius: theme.shape.borderRadius,
  },
}));

// Styled menu for better appearance
// const MenuContainer = styled(Paper)(({ theme }) => ({
//   display: "flex",
//   padding: theme.spacing(0.5),
//   gap: theme.spacing(0.5),
//   boxShadow: theme.shadows[3],
//   borderRadius: theme.shape.borderRadius,
// }));

const TextElementWidget = ({ config }: { config: TextElementSchema }) => {
  const editor = useEditor({
    extensions: [StarterKit],
    content: config.setup.text || "",
    immediatelyRender: false,
    editable: true,
  });

  return (
    <Box>
      <TipTapEditorContent editor={editor} />
      {/* <div dangerouslySetInnerHTML={{ __html: config.setup.text }} /> */}
      <ArrowPopper
        open={!!editor?.isFocused}
        placement="bottom"
        isClickAwayEnabled={false}
        content={
          <Stack>
            {editor && (
              <Button
                variant="outlined"
                size="small"
                onClick={() => editor.chain().focus().toggleBold().run()}
                sx={{
                  backgroundColor: editor.isActive("bold") ? "primary.light" : "transparent",
                  color: editor.isActive("bold") ? "primary.contrastText" : "text.primary",
                  "&:hover": {
                    backgroundColor: editor.isActive("bold") ? "primary.main" : "action.hover",
                  },
                }}>
                Bold
              </Button>
            )}
          </Stack>
        }>
        <Box />
      </ArrowPopper>
    </Box>
  );
};

export default TextElementWidget;
