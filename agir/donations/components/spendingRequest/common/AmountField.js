import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import NumberField from "@agir/front/formComponents/NumberField";
import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { displayPrice } from "@agir/lib/utils/display";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledGroupAmount = styled.div`
  display: flex;
  flex-flow: row wrap;
  gap: 0.5rem 5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
    align-items: center;
  }

  ${Card} {
    flex: 1 1 auto;
    display: inline-flex;
    flex-flow: row nowrap;
    gap: 1rem;
    font-weight: 600;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex: 0 0 auto;
      font-size: 0.875rem;
      font-weight: 700;
      color: #ea610b;
      border: none;
      box-shadow: none;
      padding: 0;
      gap: 0.5rem;

      ${RawFeatherIcon} {
        width: 1.25rem;
        height: 1.25rem;
      }
    }
  }
`;

const AmountField = (props) => {
  const { value, onChange, error, disabled, availableAmount = 0 } = props;

  const isDesktop = useIsDesktop();

  return (
    <>
      <NumberField
        currency
        large
        disabled={disabled}
        id="amount"
        name="amount"
        value={value}
        onChange={onChange}
        error={error}
        label="Montant TTC (obligatoire)"
        placeholder={displayPrice(availableAmount, true)}
      />
      <Spacer size="1rem" />
      <StyledGroupAmount>
        <Card $bordered>
          <RawFeatherIcon name="info" />
          {availableAmount > 0 ? (
            <strong>
              Le solde de votre groupe d'action est de{" "}
              {displayPrice(availableAmount)}
            </strong>
          ) : (
            <strong>Le solde de votre groupe est nul</strong>
          )}
        </Card>
        <Button
          link
          block={!isDesktop}
          color="link"
          route="spendingRequestHelp"
          icon="external-link"
          rightIcon
          target={isDesktop ? "_blank" : undefined}
          wrap={!isDesktop}
        >
          Comment augmenter le solde du GA ?
        </Button>
      </StyledGroupAmount>
    </>
  );
};

AmountField.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  onChange: PropTypes.func,
  error: PropTypes.string,
  disabled: PropTypes.bool,
  availableAmount: PropTypes.number,
};

export default AmountField;
