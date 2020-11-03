import React from "react";
import { render, cleanup, fireEvent } from "@testing-library/react";

import ActivityList from "../ActivityList";
import { requiredActionTypes } from "../RequiredActionCard";

const requiredActivity = {
  id: "required-activity",
  type: requiredActionTypes[0],
  name: requiredActionTypes[0],
  event: {
    name: "L'événement",
    routes: {
      details: "/",
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
const mockData = [requiredActivity, unrequiredActivity];

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
  it("should not render any list if props.data is empty", function () {
    const props = {
      data: [],
    };
    const component = render(<ActivityList {...props} />);
    const lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
  });
  it("should not render any list if props.include is empty", function () {
    const props = {
      data: mockData,
      include: [],
    };
    const component = render(<ActivityList {...props} />);
    const lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
  });
  it("should render only one list if props.include includes 'required' and some required activity is found in props.data", function () {
    const unrequired = [unrequiredActivity];
    const props = {
      data: unrequired,
      include: ["required"],
    };
    const component = render(<ActivityList {...props} />);
    let lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
    props.data = [requiredActivity];
    component.rerender(<ActivityList {...props} />);
    lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(1);
  });
  it("should render only one list if props.include includes 'unrequired' and some unrequired activity is found in props.data", function () {
    const required = [requiredActivity];
    const props = {
      data: required,
      include: ["unrequired"],
    };
    const component = render(<ActivityList {...props} />);
    let lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
    props.data = [unrequiredActivity];
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
      data: required,
      include: ["required"],
    };
    const component = render(<ActivityList {...props} />);
    let lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(1);
    const buttons = component.queryAllByRole("button");
    expect(buttons).toHaveLength(2);
    fireEvent.click(buttons[1]);
    lists = component.queryAllByRole("list");
    expect(lists).toHaveLength(0);
  });
});
