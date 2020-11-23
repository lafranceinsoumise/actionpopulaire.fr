import { Footer } from "./Footer";

export default {
  component: Footer,
  title: "Dashboard/Footer",
};

const Template = Footer;

export const SignedIn = Template.bind({});
SignedIn.args = {
  isSignedIn: true,
};

export const Anonymous = Template.bind({});
Anonymous.args = {
  isSignedIn: false,
};
