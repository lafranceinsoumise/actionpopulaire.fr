/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, cleanup, fireEvent } from "@testing-library/react";

import ActionCard from "../ActionCard";

describe("genericComponents/ActionCard", function () {
  afterEach(cleanup);
  it("should render props.text", async function () {
    const props = {
      name: "action-card",
      text: "Do something!",
      iconName: "alert-circle",
      confirmLabel: "Yes",
      dismissLabel: "No",
      onConfirm: () => {},
      onDismiss: () => {},
    };
    const component = render(<ActionCard {...props} />);
    const text = await component.getAllByText(props.text);
    expect(text).toHaveLength(1);
  });
  it("should render two buttons if onConfirm and onDismis are functions", async function () {
    const props = {
      name: "action-card",
      text: "Do something!",
      iconName: "alert-circle",
      confirmLabel: "Yes",
      dismissLabel: "No",
      onConfirm: jest.fn(),
      onDismiss: jest.fn(),
    };
    expect(props.onConfirm.mock.calls).toHaveLength(0);
    expect(props.onDismiss.mock.calls).toHaveLength(0);
    const component = render(<ActionCard {...props} />);
    const buttons = await component.getAllByRole("button");
    expect(buttons).toHaveLength(2);
    fireEvent.click(buttons[0]);
    expect(props.onConfirm.mock.calls).toHaveLength(1);
    expect(props.onDismiss.mock.calls).toHaveLength(0);
    fireEvent.click(buttons[1]);
    expect(props.onConfirm.mock.calls).toHaveLength(1);
    expect(props.onDismiss.mock.calls).toHaveLength(1);
  });
  it("should render two links if onConfirm and onDismis are strings", async function () {
    const props = {
      name: "action-card",
      text: "Do something!",
      iconName: "alert-circle",
      confirmLabel: "Yes",
      dismissLabel: "No",
      onConfirm: "a-link",
      onDismiss: "another-link",
    };
    const component = render(<ActionCard {...props} />);
    const link = await component.getAllByRole("link");
    expect(link).toHaveLength(2);
  });
  it("should render only one button if props.onDismiss is not a function or a string", async function () {
    const props = {
      name: "action-card",
      text: "Do something!",
      iconName: "alert-circle",
      confirmLabel: "Yes",
      dismissLabel: "No",
      onConfirm: () => {},
      onDismiss: null,
    };
    const component = render(<ActionCard {...props} />);
    const text = await component.getAllByText(props.text);
    expect(text).toHaveLength(1);
    const buttons = await component.getAllByRole("button");
    expect(buttons).toHaveLength(1);
  });
});
