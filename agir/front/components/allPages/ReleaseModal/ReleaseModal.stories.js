import { ReleaseModal } from "./ReleaseModal";

export default {
  component: ReleaseModal,
  title: "Layout/ReleaseModal/Modal",
};

const Template = ReleaseModal;

export const Default = Template.bind({});
Default.args = {
  once: false,
  isActive: true,
};
