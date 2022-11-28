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
import SelectedGroupWidget from "@agir/donations/common/SelectedGroupWidget";

const StyledPhi = styled.span`
  color: ${({ theme }) => theme.redNSP};
  font-size: 1.5em;
  font-weight: 400;
  line-height: 0.75;
`;

const StyledErrorMessage = styled.p`
  text-align: center;
  font-weight: 500;
  color: ${({ theme }) => theme.redNSP};
  padding-bottom: 2rem;
`;

const LegalParagraph = styled.p`
  max-width: 582px;
  margin: 0 auto;
  font-weight: 400;
  font-size: 0.813rem;
  color: ${({ theme }) => theme.black500};
`;

const PaymentParagraph = styled.p`
  padding: 1.5rem 0;
  max-width: 582px;
  margin: 0 auto;
  text-align: center;
  font-weight: 500;
  font-size: 0.813rem;
  color: ${({ theme }) => theme.black500};

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
    selectGroup,
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
          <h2>
            Devenir <StyledPhi>φ</StyledPhi>nanceur·euse
          </h2>
          <h4>de {beneficiary}</h4>
          <SelectedGroupWidget
            group={group}
            groups={groups}
            onChange={selectGroup}
          />
          <p>
            En devenant financeur·euse de la France insoumise, vous vous engagez
            à ce que votre contribution soit versée{" "}
            <strong>mensuellement</strong> avec un engagement{" "}
            <strong>jusqu'au mois de décembre {contributionEndYear}</strong>.
          </p>
          <p>
            Grâce à <strong>votre engagement dans la durée</strong>, vous
            permettrez à notre mouvement de mieux planifier et organiser ses
            activités au niveau local et/ou national tout au long de l’année.
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
                Vous pouvez repartir la partie restante entre{" "}
                {hasGroup ? "le groupe d'action local, " : ""}une caisse
                départementale et/ou les initiatives nationales de la France
                insoumise.
              </p>
            </>
          )}
          <p>
            Vous pouvez choisir de règler votre contribution{" "}
            <strong>mensuellement par carte bancaire</strong> ou{" "}
            <strong>en une seule fois par chèque</strong>.
          </p>
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
  contributionEndYear: PropTypes.number,
  fixedRatio: PropTypes.number,
};

export default AmountStep;
