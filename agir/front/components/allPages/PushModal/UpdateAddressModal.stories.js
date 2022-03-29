import React from "react";
import { UpdateAddressModal } from "./UpdateAddressModal";

export default {
  component: UpdateAddressModal,
  title: "Layout/PushModal/UpdateAddressModal",
};

const Template = (args) => <UpdateAddressModal {...args} />;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  isLoading: false,
  errors: null,
  initialData: null,
};
export const WithErrors = Template.bind({});
WithErrors.args = {
  ...Default.args,
  initialData: {
    address1: "25 passage Dubail",
    address2: "1er étage",
    zip: "75010",
    city: "Paris",
    country: "FR",
  },
  errors: {
    address1: "Ce n'est pas bon !",
    address2: "Non non non...",
    zip: "Quoi ?!?",
    city: "WTF!",
    country: "C'est un pays, ça ?",
    global: "Ça ne va pas du tout !",
  },
};
export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true,
};
