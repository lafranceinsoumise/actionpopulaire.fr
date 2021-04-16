import { MobileAppModal } from "./MobileAppModal";

export default {
  component: MobileAppModal,
  title: "Layout/PushModal/MobileAppModal",
};

const Template = MobileAppModal;

export const Default = Template.bind({});
Default.args = {
  referralURL: "https://referral.url",
  shouldShow: true,
  onClose: () => {},
};
