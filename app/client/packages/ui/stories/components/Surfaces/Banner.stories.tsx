import type { Meta, StoryObj } from "@storybook/react";

import Banner from "../../../components/Surfaces/Banner";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Banner> = {
  component: Banner,
  tags: ["autodocs"],
  argTypes: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Banner>;

export const ImageLeft: Story = {
  args: {
    image:
      "https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
    imageSide: "left",
    content: <p>Hello</p>,
    actions: <p>action</p>,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12044%3A133253&mode=dev",
    },
  },
};

export const ImageRight: Story = {
  args: {
    image:
      "https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
    imageSide: "right",
    content: <p>Hello</p>,
    actions: <p>action</p>,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12044%3A133253&mode=dev",
    },
  },
};

export const ImageAsBackground: Story = {
  args: {
    image:
      "https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
    imageSide: "fullBehind",
    content: <p>Hello</p>,
    actions: <p>action</p>,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12044%3A133253&mode=dev",
    },
  },
};

export const EntireBannerAsImage: Story = {
  args: {
    image:
      "https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4",
    imageSide: "full",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12044%3A133253&mode=dev",
    },
  },
};
