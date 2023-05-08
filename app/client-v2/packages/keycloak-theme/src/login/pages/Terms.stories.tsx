import { ComponentStory, ComponentMeta } from '@storybook/react';
import { createPageStory } from "../createPageStory";

const { PageStory } = createPageStory({
    pageId: "terms.ftl"
});

export default {
    title: "keycloak/Terms",
    component: PageStory,
} as ComponentMeta<typeof PageStory>;

export const Primary: ComponentStory<typeof PageStory> = () => <PageStory />;
