import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";

import { getReminder } from "@agir/donations/common/allocations.config";

import AmountWidget from "@agir/donations/common/AmountWidget";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
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
    contributionEndYear,
    fixedRatio,
  } = props;

  const [amount, setAmount] = useState(initialAmount);
  const [paymentTiming, setPaymentTiming] = useState(initialPaymentTiming);
  const [allocations, setAllocations] = useState();

  const remainder = useMemo(
    () => getReminder(allocations, amount),
    [allocations, amount]
  );

  const hasGroup = !!group?.id;
  const hasSubmit =
    !isLoading && amount && amount <= maxAmount && remainder === 0;

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
                Pour destiner une partie de votre contribution financière{" "}
                <strong>à un groupe d'action certifié</strong>, utilisez le
                bouton "financer" dans{" "}
                <Link
                  route={hasUser ? "groups" : "groupMap"}
                  params={!hasUser ? { subtype: "certifié" } : null}
                >
                  la page du groupe
                </Link>
              </span>
            </StyledGroupLink>
          ) : null}
          <h2>Devenir financeur·euse</h2>
          <h4>de {beneficiary}</h4>
          {hasGroup ? (
            <StyledGroup>
              <RawFeatherIcon name="arrow-right-circle" />
              <span>
                Groupe bénéficiaire de votre contribution&nbsp;:
                <strong>{group.name}</strong>
              </span>
            </StyledGroup>
          ) : null}
          <p>
            En devenant financeur·euse de la France insoumise, vous vous engagez
            à ce que votre contribution financière volontaire soit versée{" "}
            <strong>mensuellement</strong> avec un engagement{" "}
            <strong>jusqu'au mois de décembre {contributionEndYear}</strong>.
          </p>
          <p>
            Grâce à votre engagement dans la durée, vous permettrez à notre
            mouvement de mieux planifier et organiser ses activités au niveau
            locale et/ou nationale tout au long de l’année.
          </p>
          {fixedRatio && (
            <>
              <p>
                Une partie de cette contribution ({fixedRatio * 100}%) sera
                automatiquement reservée à une{" "}
                <Link route="contributionHelp">
                  caisse nationale de solidarité financière
                </Link>{" "}
                et sera ensuite redistribuée aux caisses départementales.
              </p>
              <p>
                Vous pouvez choisir de repartir la partie restante entre{" "}
                {hasGroup ? "le groupe d'action local, " : ""}une caisse
                départementale et/ou les initiatives nationales de la France
                insoumise.
              </p>
            </>
          )}
          <p>
            <Link route="contributionHelp">En savoir plus</Link>
          </p>
          <form noValidate onSubmit={handleSubmit}>
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
              fixedRatio={fixedRatio}
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
  contributionEndYear: PropTypes.number,
  fixedRatio: PropTypes.number,
};

export default AmountStep;
