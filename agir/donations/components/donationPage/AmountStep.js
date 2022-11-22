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

const StyledGroupLink = styled.div`
  margin: 1rem 0;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid ${(props) => props.theme.black200};
  & > span {
    flex: 1 1 auto;
  }
  ${RawFeatherIcon} {
    flex: 0 0 auto;
  }
`;

const StyledGroup = styled.div`
  margin: 1rem 0;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.default.primary50};
  color: ${(props) => props.theme.default.primary500};

  & > span {
    flex: 1 1 auto;
    font-size: 0.875rem;
    strong {
      display: block;
      font-weight: 500;
      font-size: 1rem;
      color: ${(props) => props.theme.black1000};
    }
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
  }
`;

const AmountStep = (props) => {
  const {
    isLoading,
    allowedPaymentModes,
    beneficiary,
    legalParagraph,
    externalLinkRoute,
    hasUser,
    group,
    onSubmit,
    error,
    maxAmount,
    maxAmountWarning,
    initialAmount = 0,
    initialPaymentTiming,
  } = props;

  const [amount, setAmount] = useState(initialAmount);
  const [paymentTiming, setPaymentTiming] = useState(initialPaymentTiming);
  const [allocations, setAllocations] = useState();

  const hasGroup = !!group?.id;
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
          {!hasGroup ? (
            <StyledGroupLink>
              <RawFeatherIcon name="share" />
              <span>
                <strong>Pour faire un don alloué</strong> vers un groupe
                d'action certifié, utilisez le bouton "financer" dans{" "}
                <Link
                  route={hasUser ? "groups" : "groupMap"}
                  params={!hasUser ? { subtype: "certifié" } : null}
                >
                  la page du groupe
                </Link>
              </span>
            </StyledGroupLink>
          ) : null}
          <h2>Faire un don</h2>
          <h4>à {beneficiary}</h4>
          {hasGroup ? (
            <>
              <StyledGroup>
                <RawFeatherIcon name="arrow-right-circle" />
                <span>
                  Dons alloués vers le groupe
                  <strong>{group.name}</strong>
                </span>
              </StyledGroup>
              <p>
                Pour financer ses actions, le groupe d’action certifié a la
                possibilité de se constituer une enveloppe par l’intermédiaire
                de dons alloués.{" "}
                <Link route="donationHelp">En savoir plus</Link>
              </p>
            </>
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
                <strong>Suivant</strong>
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
  hasUser: PropTypes.bool,
  group: PropTypes.object,
  beneficiary: PropTypes.string,
  legalParagraph: PropTypes.string,
  externalLinkRoute: PropTypes.string,
  isLoading: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  error: PropTypes.string,
  maxAmount: PropTypes.number,
  maxAmountWarning: PropTypes.node,
  initialAmount: PropTypes.number,
  initialPaymentTiming: PropTypes.string,
  allowedPaymentModes: PropTypes.object.isRequired,
};

export default AmountStep;
