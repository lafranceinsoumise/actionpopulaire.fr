import React from "react";
import { render, cleanup, fireEvent } from "@testing-library/react";

import { ActivityList } from "../ActivityList";
import { requiredActionTypes } from "../RequiredActionCard";

const requiredActivity = {
  id: "required-activity",
  type: requiredActionTypes[0],
  name: requiredActionTypes[0],
  event: {
    name: "L'événement",
    routes: {
      details: "/",
      manage: "/",
      join: "/",
    },
  },
  supportGroup: {
    name: "Le Groupe",
    url: "/",
  },
  individual: {
    fullName: "Foo Bar",
    email: "foo@bar.com",
  },
};
const unrequiredActivity = {
  ...requiredActivity,
  id: "unrequired-activity",
  type: "not-" + requiredActionTypes[0],
  name: "not-" + requiredActionTypes[0],
};

jest.mock("@agir/front/genericComponents/GobalContext", () => ({
  useGlobalContext: () => ({
    dispatch: () => {},
  }),
}));
jest.mock("../ActivityCard", () => {
  const ActivityCard = () => <div id="activity-card" />;
  ActivityCard.displayName = "ActivityCard";
  return {
    __esModule: true,
    default: ActivityCard,
  };
});

describe("genericComponents/ActivityList", function () {
  afterEach(cleanup);
  it("should not render any list if props.required and props.unrequired are empty", function () {
    const props = {
      required: [],
      unrequired: [],
    };
    const component = render(<ActivityList {...props} />);
    const lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
  });
  it("should render only one list if props.required is not empty but props.unrequired is", function () {
    const props = {
      required: [],
      unrequired: [],
    };
    const component = render(<ActivityList {...props} />);
    let lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
    props.required = [requiredActivity];
    component.rerender(<ActivityList {...props} />);
    lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(1);
  });
  it("should render only one list if props.unrequired is not empty but props.required is", function () {
    const props = {
      unrequired: [],
      required: [],
    };
    const component = render(<ActivityList {...props} />);
    let lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
    props.unrequired = [unrequiredActivity];
    component.rerender(<ActivityList {...props} />);
    lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(1);
  });
  it("should pass required activity list items a function to dismiss them", function () {
    const required = [
      {
        ...requiredActivity,
        type: "new-member",
      },
    ];
    const props = {
      required: required,
      onDismiss: jest.fn(),
    };
    expect(props.onDismiss.mock.calls).toHaveLength(0);
    const component = render(<ActivityList {...props} />);
    let lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(1);
    const buttons = component.queryAllByRole("button");
    expect(buttons).toHaveLength(2);
    fireEvent.click(buttons[1]);
    expect(props.onDismiss.mock.calls).toHaveLength(1);
  });
});
