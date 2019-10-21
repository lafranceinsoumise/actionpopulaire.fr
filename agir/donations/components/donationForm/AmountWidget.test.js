import React from "react";
import renderer from "react-test-renderer";

import AmountWidget from "./AmountWidget";

test("AmountWidget dans son état initial", () => {
  const component = renderer.create(
    <AmountWidget amount={null} error={null} />
  );

  expect(component.toJSON()).toMatchSnapshot();
});

test("AmountWidget avec un montant sélectionné", () => {
  const component = renderer.create(<AmountWidget amount={50} error={null} />);

  expect(component.toJSON()).toMatchSnapshot();
});

test("Sélectionner des valeurs dans le AmountWidget", () => {
  let currentValue = null;

  const component = renderer.create(
    <AmountWidget
      amount={null}
      onAmountChange={amount => (currentValue = amount)}
      error={null}
    />
  );
  // let's click on the 20 € button
  const button50 = component.root.find(
    c => c.props.children && c.props.children[0] === 50
  );

  button50.props.onClick();

  expect(currentValue).toEqual(50);
});
