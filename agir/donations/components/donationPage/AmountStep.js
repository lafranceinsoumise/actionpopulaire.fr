import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import AmountWidget from "@agir/donations/common/AmountWidget";
import {
  Link,
  StepButton,
  StyledIllustration,
  StyledBody,
  StyledPage,
  StyledLogo,
  StyledMain,
} from "@agir/donations/common/StyledComponents";

import acceptedPaymentMethods from "@agir/donations/common/images/accepted-payment-methods.svg";
import SelectedGroupWidget from "../common/SelectedGroupWidget";

const StyledErrorMessage = styled.p`
  text-align: center;
  font-weight: 500;
  color: ${(props) => props.theme.redNSP};
  padding-bottom: 2rem;
`;

const LegalParagraph = styled.p`
  max-width: 582px;
  margin: 0 auto;
  font-weight: 400;
  font-size: 0.813rem;
  color: ${(props) => props.theme.black500};
`;

const PaymentParagraph = styled.p`
  padding: 1.5rem 0;
  max-width: 582px;
  margin: 0 auto;
  text-align: center;
  font-weight: 500;
  font-size: 0.813rem;
  color: ${(props) => props.theme.black500};
  & > span {
    display: flex;
    justify-content: center;
    align-items: center;
    padding-bottom: 1.5rem;
  }
`;

const AmountStep = (props) => {
  const {
    isLoading,
    allowedPaymentModes,
    beneficiary,
    legalParagraph,
    externalLinkRoute,
    group,
    groups,
    onSubmit,
    selectGroup,
    error,
    maxAmount,
    maxAmountWarning,
    initialAmount = 0,
    initialPaymentTiming,
    hasAllocations = true,
  } = props;

  const [amount, setAmount] = useState(initialAmount);
  const [paymentTiming, setPaymentTiming] = useState(initialPaymentTiming);
  const [allocations, setAllocations] = useState();

  const hasSubmit = !isLoading && amount && amount <= maxAmount;

  const handleSubmit = (e) => {
    e.preventDefault();
    const totalAmount = Math.round(amount * 100) / 100;
    onSubmit({
      amount: totalAmount,
      paymentTiming,
      allocations,
    });
  };

  const allowedPaymentTimings = Object.keys(allowedPaymentModes);

  return (
    <StyledPage>
      <StyledIllustration aria-hidden="true" />
      <StyledBody>
        <StyledMain>
          <StyledLogo
            alt={`Logo ${beneficiary}`}
            route={externalLinkRoute}
            rel="noopener noreferrer"
            target="_blank"
          />
          <h2>Faire un don</h2>
          <h4>à {beneficiary}</h4>
          {hasAllocations && (
            <SelectedGroupWidget
              group={group}
              groups={groups}
              onChange={selectGroup}
            />
          )}
          {hasAllocations && group?.id ? (
            <p>
              Pour financer ses actions, le groupe d’action certifié a la
              possibilité de se constituer une enveloppe par l’intermédiaire de
              dons alloués. <Link route="donationHelp">En savoir plus</Link>
            </p>
          ) : (
            <>
              <p>
                Chaque don nous aide à l’organisation d’événements, à l’achat de
                matériel, au fonctionnement de ce site, etc.
              </p>
              <p>
                Nous avons besoin du soutien financier de chacun·e d’entre vous.
              </p>
            </>
          )}
          <form onSubmit={handleSubmit}>
            <AmountWidget
              disabled={isLoading}
              amount={amount}
              maxAmount={maxAmount}
              maxAmountWarning={maxAmountWarning}
              paymentTiming={paymentTiming}
              allocations={allocations}
              groupId={group?.id}
              onChangeAmount={setAmount}
              onChangePaymentTiming={setPaymentTiming}
              onChangeAllocations={setAllocations}
              allowedPaymentTimings={allowedPaymentTimings}
              hasAllocations={hasAllocations}
            />
            {!isLoading && error ? (
              <StyledErrorMessage>{error}</StyledErrorMessage>
            ) : null}
            <StepButton
              block
              type="submit"
              disabled={!hasSubmit}
              loading={isLoading}
            >
              <span>
                <strong>Continuer</strong>
                <br />
                1/3 étapes
              </span>
              <RawFeatherIcon name="arrow-right" />
            </StepButton>
          </form>
          <hr />
          <LegalParagraph>{legalParagraph}</LegalParagraph>
          <PaymentParagraph>
            <span>
              <RawFeatherIcon width="1rem" height="1rem" name="lock" />
              &ensp;SÉCURISÉ ET ANONYME
            </span>
            <img
              width="366"
              height="26"
              src={acceptedPaymentMethods}
              alt="Moyens de paiement acceptés : Visa, Visa Electron, Mastercard, Maestro, Carte Bleue, E-Carte Bleue"
            />
          </PaymentParagraph>
        </StyledMain>
      </StyledBody>
    </StyledPage>
  );
};

AmountStep.propTypes = {
  group: PropTypes.object,
  groups: PropTypes.array,
  beneficiary: PropTypes.string,
  legalParagraph: PropTypes.string,
  externalLinkRoute: PropTypes.string,
  isLoading: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  selectGroup: PropTypes.func,
  error: PropTypes.string,
  maxAmount: PropTypes.number,
  maxAmountWarning: PropTypes.node,
  initialAmount: PropTypes.number,
  initialPaymentTiming: PropTypes.string,
  allowedPaymentModes: PropTypes.object.isRequired,
  hasAllocations: PropTypes.bool,
};

export default AmountStep;
