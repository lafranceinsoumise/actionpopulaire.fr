import React from "react";

import CONFIG from "@agir/front/dashboardComponents/navigation.config";
import Navigation from "./Navigation";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import { activityStatus } from "@agir/activity/common/helpers";

const mockRoutes = [
  ...CONFIG.menuLinks.map((link) => link.route),
  ...CONFIG.menuLinks.map((link) =>
    link.secondaryLinks
      ? [
          {
            id: `${link.id}__seclink`,
            label: `${link.title} — lien secondaire`,
            href: link.secondaryLinks,
          },
        ]
      : null
  ),
  ...CONFIG.secondaryLinks.map((link) => link.route),
]
  .filter(Boolean)
  .reduce(
    (obj, link) => ({
      ...obj,
      [Array.isArray(link) ? link[0].href : link]: link,
    }),
    {}
  );

export default {
  component: Navigation,
  title: "Dashboard/Navigation",
};

const Template = (args) => (
  <TestGlobalContextProvider
    value={{
      routes: mockRoutes,
      activities: Object.keys([...Array(args.unreadActivityCount)]).map(
        (i) => ({
          id: i,
          status: activityStatus.STATUS_UNDISPLAYED,
        })
      ),
      requiredActionActivities: Object.keys([
        ...Array(args.requiredActionActivityCount),
      ]),
    }}
  >
    <Navigation {...args} />
  </TestGlobalContextProvider>
);

export const Default = Template.bind({});
Default.args = {
  active: "events",
  requiredActionActivityCount: 1,
  unreadActivityCount: 10,
};
Default.argTypes = {
  requiredActionActivityCount: { type: "number", min: 0 },
  unreadActivityCount: { type: "number", min: 0 },
};
