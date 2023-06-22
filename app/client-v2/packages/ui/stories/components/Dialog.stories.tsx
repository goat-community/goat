import type { Meta, StoryObj } from "@storybook/react/dist";
import React from "react";

import Dialog from "../../components/Dialog";
import { Button } from "../theme";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Dialog> = {
  component: Dialog,
  tags: ["autodocs"],
  argTypes: {},
  args: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Dialog>;

export const DialogOnLeft: Story = () => {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);

  const actionHeader = (
    <>
      <Button onClick={() => setAnchorEl(null)} variant="noBorder">
        CANCEL
      </Button>
      <Button onClick={() => setAnchorEl(null)} variant="noBorder">
        CONFIRM
      </Button>
    </>
  );

  function openDialogInitializer(event: React.MouseEvent<HTMLButtonElement>) {
    setAnchorEl(event.currentTarget);
  }

  function closeTablePopover() {
    setAnchorEl(null);
  }

  return (
    <>
      <Button variant="secondary" onClick={openDialogInitializer}>
        Open Dialog Left
      </Button>
      {anchorEl ? (
        <Dialog
          anchorEl={anchorEl}
          onClick={closeTablePopover}
          title="Sample Header"
          width="444px"
          direction="left"
          action={actionHeader}>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptas, nesciunt.
        </Dialog>
      ) : null}
    </>
  );
};

export const DialogOnRight: Story = () => {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);

  const actionHeader = (
    <>
      <Button onClick={() => setAnchorEl(null)} variant="noBorder">
        CANCEL
      </Button>
      <Button onClick={() => setAnchorEl(null)} variant="noBorder">
        CONFIRM
      </Button>
    </>
  );

  function openDialogInitializer(event: React.MouseEvent<HTMLButtonElement>) {
    setAnchorEl(event.currentTarget);
  }

  function closeTablePopover() {
    setAnchorEl(null);
  }

  return (
    <>
      <Button variant="secondary" onClick={openDialogInitializer}>
        Open Dialog Right
      </Button>
      {anchorEl ? (
        <Dialog
          anchorEl={anchorEl}
          onClick={closeTablePopover}
          title="Sample Header"
          width="444px"
          direction="right"
          action={actionHeader}>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptas, nesciunt.
        </Dialog>
      ) : null}
    </>
  );
};

DialogOnLeft.args = {};
DialogOnRight.args = {};
