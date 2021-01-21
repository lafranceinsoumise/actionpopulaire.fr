import Modal from "./Modal";

export default {
  component: Modal,
  title: "Form/MessageModal/Modal",
};

const Template = Modal;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  onClose: () => {},
  onSend: () => {},
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
    fullName: "Bill Murray",
    avatar: "https://www.fillmurray.com/200/200",
  },
  isLoading: false,
};

export const WithInitialData = Template.bind({});
WithInitialData.args = {
  ...Default.args,
  message: {
    id: "b",
    linkedEvent: {
      id: "a",
      name: "Event A",
      startTime: "2021-01-09 10:04:19",
      type: "G",
    },
    content: "Bonjour !",
  },
};

export const Loading = Template.bind({});
Loading.args = {
  ...WithInitialData.args,
  isLoading: true,
};
