import React from "react";

import GroupCard from "./GroupCard";
import { decorateArgs } from "@agir/lib/utils/storyUtils";
import { DateTime } from "luxon";

export default {
  component: GroupCard,
  title: "Groupes/GroupCard",
  argTypes: {
    routes: { table: { disable: true } },
    discountCodes: { control: { type: "object" } },
  },
  decorators: [
    (story) => (
      <div style={{ margin: "1em", maxWidth: "800px" }}>{story()}</div>
    ),
  ],
};

const setRoutes = ({ fund, manage, ...args }) => ({
  ...args,
  routes: {
    page: "#page",
    fund: fund ? "#fund" : undefined,
    manage: manage ? "#manage" : undefined,
  },
});

const convertDates = ({ discountCodes, ...args }) => ({
  ...args,
  discountCodes:
    discountCodes &&
    discountCodes.map(({ code, expirationDate }) => ({
      code,
      expirationDate: DateTime.fromISO(expirationDate),
    })),
});

const Template = decorateArgs(setRoutes, convertDates, GroupCard);

const DEFAULT_DESCRIPTION = `
<p>I hate yogurt. It's just stuff with bits in. You hate me; you want to kill me! Well, go on! Kill me! KILL ME! You've swallowed a planet! The way I see it, every life is a pile of good things and bad things.…hey.…the good things don't always soften the bad things; but vice-versa the bad things don't necessarily spoil the good things and make them unimportant.</p>
<ol>
    <li>The way I see it, every life is a pile of good things and bad things.…hey.…the good things don't always soften the bad things; but vice-versa the bad things don't necessarily spoil the good things and make them unimportant.</li><li>It's art! A statement on modern society, 'Oh Ain't Modern Society Awful?'!</li><li>All I've got to do is pass as an ordinary human being. Simple. What could possibly go wrong?</li>
</ol>
<p>I'm the Doctor, I'm worse than everyone's aunt. *catches himself* And that is not how I'm introducing myself. It's a fez. I wear a fez now. Fezes are cool. The way I see it, every life is a pile of good things and bad things.…hey.…the good things don't always soften the bad things; but vice-versa the bad things don't necessarily spoil the good things and make them unimportant.</p>
<ul>
    <li>They're not aliens, they're Earth…liens!</li><li>I am the last of my species, and I know how that weighs on the heart so don't lie to me!</li><li>You hate me; you want to kill me! Well, go on! Kill me! KILL ME!</li>
</ul>
`;

const today = DateTime.local();

export const Default = Template.bind({});
Default.args = {
  id: "12345",
  name: "Prout",
  description: DEFAULT_DESCRIPTION,
  eventCount: 7,
  membersCount: 14,
  typeLabel: "Groupe fonctionnel",
  labels: ["Groupe certifié", "Espace opérationnel"],
  fund: true,
  manage: true,
  displayGroupLogo: true,
  displayType: true,
  displayDescription: true,
  displayMembership: true,
  isMember: false,
  is2022: false,
  routes: {
    page: "#groupe",
  },
};

export const OnMyGroupsPage = Template.bind({});
OnMyGroupsPage.args = {
  ...Default.args,
  description: undefined,
  typeLabel: undefined,
  labels: undefined,
  displayGroupLogo: false,
  displayType: false,
  displayDescription: false,
  displayMembership: false,
  discountCodes: [
    {
      code: "ZEziAujKIhjBJhjHuhguyuY",
      expirationDate: today.plus({ days: 11 }).toISODate(),
    },
    {
      code: "ZxlOienNQWopwoZuZnAzI",
      expirationDate: today.plus({ days: 42 }).toISODate(),
    },
  ],
};
