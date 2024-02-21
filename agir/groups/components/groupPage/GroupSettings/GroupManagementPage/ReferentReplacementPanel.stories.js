import React from "react";

import MOCK_GROUP from "@agir/front/mockData/group";
import ReferentReplacementPanel from "./ReferentReplacementPanel";

const MEMBERS = [
  {
    id: 0,
    displayName: "Foo Bar",
    email: "admin@example.fr",
    membershipType: 5,
    image: "https://loremflickr.com/200/200/1",
    created: "2020-01-01 00:00:00",
    updated: "2020-01-01 00:00:00",
  },
  {
    id: 1,
    displayName: "Bar Baz",
    email: "admin@example.fr",
    membershipType: 10,
    image: "https://loremflickr.com/200/200/2",
    created: "2021-01-01 00:00:00",
    updated: "2021-01-01 00:00:00",
  },
  {
    id: 2,
    displayName: "Baz Qux",
    email: "admin@example.fr",
    membershipType: 50,
    image: "https://loremflickr.com/200/200/3",
    created: "2022-01-01 00:00:00",
    updated: "2022-01-01 00:00:00",
    onResetMembershipType: console.log,
  },
  {
    id: 3,
    displayName: "Qux Quux",
    email: "admin@example.fr",
    membershipType: 100,
    image: "https://loremflickr.com/200/200/4",
    created: "2023-01-01 00:00:00",
    updated: "2023-01-01 00:00:00",
  },
];

export default {
  component: ReferentReplacementPanel,
  title: "GroupSettings/ReferentReplacementPanel",
};

const Template = (args) => {
  const [isLoading, setIsLoading] = React.useState(args.isLoading);
  const [error, setError] = React.useState("");
  const [isDone, setIsDone] = React.useState(false);

  const handleSubmit = React.useCallback(() => {
    setError("");
    setIsLoading(true);
    setTimeout(
      () => {
        setIsLoading(false);
        if (args.error) {
          setError(args.error);
        } else {
          setIsDone(true);
        }
      },
      Math.random() * 5000 + 200,
    );
  }, [args.error]);

  return (
    <div style={{ padding: "1.5rem" }}>
      <ReferentReplacementPanel
        {...args}
        isLoading={isLoading}
        error={error}
        isDone={isDone}
        onSubmit={handleSubmit}
        onBack={() => {}}
      />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  group: MOCK_GROUP,
  members: MEMBERS,
  leavingMember: MEMBERS[3],
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true,
};

export const WithError = Template.bind({});
WithError.args = {
  ...Default.args,
  error: "Une erreur est survenue",
};
