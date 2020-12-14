import Steps, { Step, steps } from "./Steps";

export default {
  component: Steps,
  title: "Layout/PushModal/ReleaseModal/Steps",
};

const noop = () => {};

export const Default = Steps.bind({});
Default.args = {
  onClose: noop,
};
export const Step_1 = Step.bind({});
Step_1.args = {
  ...steps[0],
  onClick: noop,
  hasNext: true,
};
export const Step_2 = Step.bind({});
Step_2.args = {
  ...steps[1],
  onClick: noop,
  hasNext: true,
};
export const Step_3 = Step.bind({});
Step_3.args = {
  ...steps[2],
  onClick: noop,
  hasNext: true,
};
export const Step_4 = Step.bind({});
Step_4.args = {
  ...steps[3],
  onClick: noop,
  hasNext: true,
};
export const Step_5 = Step.bind({});
Step_5.args = {
  ...steps[4],
  onClick: noop,
  hasNext: false,
};
