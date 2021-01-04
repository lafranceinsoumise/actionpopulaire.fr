import React from "react";

import Activities from "@agir/activity/common/Activities";
import RequiredActionCard from "./RequiredActionCard";

import * as RequiredActionCardStories from "./RequiredActionCard.stories";

export default {
  component: Activities,
  title: "Activities/RequiredActivityList",
};

const Template = (args) => {
  const [activities, setActivites] = React.useState(args.activities);

  const handleDismiss = React.useCallback((id) => {
    setActivites((state) => state.filter((activity) => activity.id !== id));
  }, []);

  return (
    <>
      <button
        disabled={activities.length >= args.activities.length}
        onClick={() => setActivites(args.activities)}
      >
        Reset activities
      </button>
      <Activities
        CardComponent={RequiredActionCard}
        activities={activities}
        onDismiss={handleDismiss}
      />
    </>
  );
};

const initialActivities = Object.values(RequiredActionCardStories)
  .map(({ args }, i) => ({ ...args, id: i }))
  .filter(Boolean);

export const Default = Template.bind({});
Default.args = {
  activities: initialActivities,
};

export const Empty = Template.bind({});
Empty.args = {
  activities: [],
};
