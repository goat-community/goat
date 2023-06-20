import type { Meta, StoryObj } from "@storybook/react/dist";
import { useState } from "react";

import Modal from "../../components/Modal";
import { ThemeProvider } from "../theme";
import { Button, Text } from "../theme";

const meta: Meta<typeof Modal> = {
  component: Modal,
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
type Story = StoryObj<typeof Modal>;

export const ModalFullOption: Story = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const handleClick = () => {
    setIsVisible(true);
  };

  const menuHeader = <Text typo="object heading">Header</Text>;

  const actionHeader = (
    <>
      <Button onClick={() => setIsVisible(false)} variant="noBorder">
        CANCEL
      </Button>
      <Button onClick={() => setIsVisible(false)} variant="noBorder">
        CONFIRM
      </Button>
    </>
  );

  return (
    <>
      <Button variant="ternary" onClick={handleClick}>
        Modal
      </Button>
      <Modal
        width="444px"
        open={isVisible}
        changeOpen={setIsVisible}
        action={actionHeader}
        header={menuHeader}>
        <Text typo="body 2">
          By removing a user they won&apos;t be able to access any projects under your organisation
        </Text>
      </Modal>
    </>
  );
};

export const ModalWithoutHeader: Story = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const handleClick = () => {
    setIsVisible(true);
  };

  const actionHeader = (
    <>
      <Button onClick={() => setIsVisible(false)} variant="noBorder">
        CANCEL
      </Button>
      <Button onClick={() => setIsVisible(false)} variant="noBorder">
        CONFIRM
      </Button>
    </>
  );

  return (
    <>
      <Button variant="ternary" onClick={handleClick}>
        Without Header
      </Button>
      <Modal width="444px" open={isVisible} changeOpen={setIsVisible} action={actionHeader}>
        <Text typo="body 2">
          By removing a user they won&apos;t be able to access any projects under your organisation
        </Text>
      </Modal>
    </>
  );
};

export const ModalWithoutAction: Story = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const handleClick = () => {
    setIsVisible(true);
  };

  const menuHeader = <Text typo="object heading">Header</Text>;

  return (
    <>
      <Button variant="ternary" onClick={handleClick}>
        Without Action
      </Button>
      <Modal width="444px" open={isVisible} changeOpen={setIsVisible} header={menuHeader}>
        <Text typo="body 2">
          By removing a user they won&apos;t be able to access any projects under your organisation
        </Text>
      </Modal>
    </>
  );
};

export const ModalOnlyBody: Story = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const handleClick = () => {
    setIsVisible(true);
  };

  return (
    <>
      <Button variant="ternary" onClick={handleClick}>
        Only Body
      </Button>
      <Modal width="444px" open={isVisible} changeOpen={setIsVisible}>
        <Text typo="body 2">
          By removing a user they won&apos;t be able to access any projects under your organisation
        </Text>
      </Modal>
    </>
  );
};

ModalFullOption.args = {};
ModalWithoutHeader.args = {};
ModalWithoutAction.args = {};
ModalOnlyBody.args = {};
