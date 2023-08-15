import type { StoryFn, Meta } from "@storybook/react";

import { createPageStory } from "../login/createPageStory";

const pageId = "register-user-profile.ftl";

const { PageStory } = createPageStory({ pageId });

export default {
  title: "Pages/Auth/RegisterUserProfile",
  component: PageStory,
} as Meta<typeof PageStory>;

export const Default: StoryFn<typeof PageStory> = () => <PageStory />;
