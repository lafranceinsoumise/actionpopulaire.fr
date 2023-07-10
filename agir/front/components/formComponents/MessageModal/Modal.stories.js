import React from "react";
import Modal from "./Modal";

export default {
  component: Modal,
  title: "Form/MessageModal/Modal",
};

const Template = Modal;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  loadMoreEvents: () => {},
  events: [
    {
      id: "a",
      name: "Event A",
      startTime: "2021-01-09 10:04:19",
      type: "G",
    },
    {
      id: "b",
      name: "Event B",
      startTime: "2021-01-09 10:04:19",
      type: "M",
    },
    {
      id: "c",
      name: "Event C",
      startTime: "2021-01-09 10:04:19",
      type: "A",
    },
  ],
  message: null,
  user: {
    displayName: "Bill Murray",
    image: "https://loremflickr.com/200/200",
  },
  isLoading: false,
};

const WithGroupStepModal = (args) => {
  const { events } = args;
  const [groupEvents, setGroupEvents] = React.useState([]);
  const handleSelectGroup = React.useCallback(
    (selectedGroup) => {
      setGroupEvents(
        events.filter(
          (event) =>
            Array.isArray(event.groups) &&
            event.groups.some((group) => group.id === selectedGroup.id)
        )
      );
    },
    [events]
  );

  return (
    <Template
      {...args}
      events={groupEvents}
      onSelectGroup={handleSelectGroup}
    />
  );
};
export const WithGroupStep = WithGroupStepModal.bind({});
WithGroupStep.args = {
  ...Default.args,
  events: [
    {
      id: "a",
      name: "Group A Event",
      startTime: "2021-01-09 10:04:19",
      type: "G",
      groups: [{ id: "a" }],
    },
    {
      id: "b",
      name: "Group B Event",
      startTime: "2021-01-09 10:04:19",
      type: "G",
      groups: [{ id: "b" }],
    },
    {
      id: "c",
      name: "Group A and B Event",
      startTime: "2021-01-09 10:04:19",
      type: "G",
      groups: [{ id: "a" }, { id: "b" }],
    },
  ],
  groups: [
    {
      id: "a",
      name: "Groupe A",
    },
    {
      id: "b",
      name: "Équipe B",
    },
  ],
};

export const WithInitialData = Template.bind({});
WithInitialData.args = {
  ...Default.args,
  message: {
    id: "b",
    group: {
      id: "b",
      name: "Équipe B",
    },
    linkedEvent: {
      id: "a",
      name: "Event A",
      startTime: "2021-01-09 10:04:19",
      type: "G",
    },
    subject: "Un beau message",
    text: "Bonjour !",
  },
};

export const Loading = Template.bind({});
Loading.args = {
  ...WithInitialData.args,
  isLoading: true,
};
