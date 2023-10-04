import React from "react";

import CategoryCard from "./CategoryCard";
import { CATEGORY_OPTIONS } from "./form.config";

export default {
  component: CategoryCard,
  title: "Donations/SpendingRequest/CategoryCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <CategoryCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  category: Object.values(CATEGORY_OPTIONS)[3].value,
};

export const Legacy = Template.bind({});
Legacy.args = {
  category: "X",
};
