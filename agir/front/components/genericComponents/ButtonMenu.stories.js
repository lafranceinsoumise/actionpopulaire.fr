import React from "react";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Popin from "@agir/front/genericComponents/BottomSheet";

import ButtonMenu from "./ButtonMenu";

export default {
  component: ButtonMenu,
  title: "Generic/ButtonMenu",
};

const Template = (args) => (
  <p
    style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      margin: "2rem",
    }}
  >
    <span style={{ fontSize: "3rem" }}>⟶&nbsp;</span>
    <ButtonMenu {...args}>
      <ul>
        <li>
          <button>An action</button>
        </li>
        <li>
          <button>Another action</button>
        </li>
      </ul>
    </ButtonMenu>
    <span style={{ fontSize: "3rem" }}>&nbsp;⟵</span>
  </p>
);

export const Default = Template.bind({});
Default.args = {
  text: "Bouton menu",
};

export const Success = Template.bind({});
Success.args = {
  text: "Bouton menu",
  icon: "check-circle",
  color: "success",
};

export const WithBottomSheet = Template.bind({});
WithBottomSheet.args = {
  text: "Bouton menu",
  icon: "x",
  color: "danger",
  DesktopLayout: BottomSheet,
  MobileLayout: Popin,
};
