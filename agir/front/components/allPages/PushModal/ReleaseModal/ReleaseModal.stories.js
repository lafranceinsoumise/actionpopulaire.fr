import { ReleaseModal } from "./ReleaseModal";

export default {
  component: ReleaseModal,
  title: "Layout/PushModal/ReleaseModal",
};

const Template = ReleaseModal;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  onClose: () => {},
};
