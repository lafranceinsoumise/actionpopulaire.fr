/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, cleanup } from "@testing-library/react";

import Announcement from "../Announcement";

describe("genericComponents/Announcement", function () {
  afterEach(cleanup);
  it("should render props.image if defined", async function () {
    const props = {
      title: "title",
      content: "content",
      image: {
        desktop: "desktop",
        mobile: "mobile",
      },
      link: "link",
    };
    const component = render(<Announcement {...props} />);
    let imageBlock = await component.queryAllByLabelText(props.title);
    expect(imageBlock).toHaveLength(1);
    component.rerender(<Announcement {...props} image={null} />);
    imageBlock = await component.queryAllByLabelText(props.title);
    expect(imageBlock).toHaveLength(0);
  });
  it("should render props.title", async function () {
    const props = {
      title: "title",
      content: "content",
      image: {
        desktop: "desktop",
        mobile: "mobile",
      },
      link: "link",
    };
    const component = render(<Announcement {...props} />);
    const text = await component.getAllByText(props.title);
    expect(text).toHaveLength(1);
  });
  it("should render props.content", async function () {
    const props = {
      title: "title",
      content: "content",
      image: {
        desktop: "desktop",
        mobile: "mobile",
      },
      link: "link",
    };
    const component = render(<Announcement {...props} />);
    const text = await component.getAllByText(props.content);
    expect(text).toHaveLength(1);
  });
});
