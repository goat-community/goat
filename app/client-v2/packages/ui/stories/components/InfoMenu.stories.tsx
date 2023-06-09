import type { Meta, StoryObj } from "@storybook/react";
import { useState, useRef } from "react";

import { InfoMenu } from "../../components/InfoMenu";
import { ThemeProvider } from "../theme";
import { Icon } from "../theme";
import { Text } from "../theme";
import { Button } from "../theme";

const meta: Meta<typeof InfoMenu> = {
  component: InfoMenu,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    children: {
      control: false,
    },
    status: {
      control: {
        type: "boolean",
      },
    },
    menuActions: {
      control: false,
    },
    menuHeader: {
      control: false,
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof HTMLDivElement>;

export const Primary: Story = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const ButtonElement = useRef(null);

  const handleClick = () => {
    setIsVisible(true);
  };
  const handleClose = () => {
    setIsVisible(false);
  };

  const menuHeader = <Text typo="object heading">Header</Text>;

  const actionHeader = <Button>Action</Button>;

  return (
    <>
      <button style={{ position: "relative" }} onClick={handleClick} ref={ButtonElement}>
        Toggle Info Menu
      </button>
      <InfoMenu
        ref={ButtonElement}
        handleCloseFunction={handleClose}
        status={isVisible}
        menuHeader={menuHeader}
        menuActions={actionHeader}>
        <Text typo="body 1">this is a simple menu info</Text>
      </InfoMenu>
    </>
  );
};

export const Secondary: Story = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const ButtonElement = useRef(null);

  const handleClick = () => {
    setIsVisible(true);
  };
  const handleClose = () => {
    setIsVisible(false);
  };

  const menuHeader = (
    <span style={{ display: "flex", alignItems: "center" }}>
      <span style={{ marginRight: "5px" }}>
        <Icon iconId="coorperate" />
      </span>{" "}
      <Text typo="body 2">GOAT</Text>
    </span>
  );

  const actionHeader = <Button startIcon="powerOff">Log Out</Button>;

  return (
    <>
      <button style={{ position: "relative" }} onClick={handleClick} ref={ButtonElement}>
        Toggle Info Menu
      </button>
      <InfoMenu
        ref={ButtonElement}
        handleCloseFunction={handleClose}
        status={isVisible}
        menuHeader={menuHeader}
        menuActions={actionHeader}>
        <Text typo="body 1">randomuser@outlook.com</Text>
        <Text typo="caption">Admin</Text>
      </InfoMenu>
    </>
  );
};

Primary.args = {};
Secondary.args = {};
