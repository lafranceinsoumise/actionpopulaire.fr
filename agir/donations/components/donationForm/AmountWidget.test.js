import React from "react";
import renderer from "react-test-renderer";

import AmountWidget from "./AmountWidget";

test("AmountWidget looks the right way", () => {
  let currentValue = null,
    component;

  component = renderer.create(
    <AmountWidget
      amount={null}
      onAmountChange={amount => (currentValue = amount)}
      error={null}
    />
  );

  expect(component.toJSON()).toMatchSnapshot();

  // let's click on the 20 € button
  const button50 = component.root.find(
    c => c.props.children && c.props.children[0] === 50
  );

  button50.props.onClick();

  expect(currentValue).toEqual(50);

  component = renderer.create(
    <AmountWidget
      amount={50}
      onAmountChange={amount => (currentValue = amount)}
      error={null}
    />
  );

  expect(component.toJSON()).toMatchSnapshot();
});
