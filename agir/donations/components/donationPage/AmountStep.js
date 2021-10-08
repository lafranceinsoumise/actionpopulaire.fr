import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import CONFIG from "./config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import AmountWidget from "./AmountWidget";
import { Link, StepButton, Theme } from "./StyledComponents";

import acceptedPaymentMethods from "./images/accepted-payment-methods.svg";

const StyledLogo = styled(Link)`
  display: block;
  width: calc(100% + 3rem);
  padding: 1rem 1.5rem;
  margin: -1rem -1.5rem 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0 -1.5rem 1rem;
    padding: 1rem;
    border-bottom: 1px solid ${(props) => props.theme.black100};
  }

  &::after {
    content: "";
    display: block;
    height: ${(props) => props.theme.logoHeight};
    background-image: url(${(props) => props.theme.logo});
    background-repeat: no-repeat;
    background-position: center center;
    background-size: contain;
  }
`;

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

const StyledMain = styled.main`
  margin: 0 auto;
  padding: 0 1.5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 630px;
  }

  h2 {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.5;
  }

  h4 {
    font-weight: 500;
    font-size: 1rem;
    margin: 0 0 1rem;
    line-height: 1.4;
  }

  hr {
    display: block;
    max-width: 582px;
    margin: 1.5rem auto;
    color: ${(props) => props.theme.black50};
  }

  p {
    margin-bottom: 0;
  }

  p + p {
    margin-top: 0.5rem;
  }

  form {
    ${StepButton} {
      margin: 0 auto;
      max-width: 400px;
      height: 80px;
      padding: 0 4.5rem;

      & > span {
        font-weight: 400;
        font-size: 0.875rem;

        strong {
          font-weight: 600;
          font-size: 1.25rem;
        }
      }

      ${RawFeatherIcon} {
        position: absolute;
        right: 1.5rem;
      }
    }
  }
`;

const StyledIllustration = styled.div``;
const StyledBody = styled.div``;
const StyledPage = styled.div`
  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  ${StyledIllustration} {
    flex: 0 0 524px;
    height: 100%;
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center center;
    background-image: url(${(props) => props.theme.illustration.large});

    @media (max-width: ${(props) => props.theme.collapse}px) {
      content: url(${(props) => props.theme.illustration.small});
      width: 100%;
      height: auto;
    }
  }

  ${StyledBody} {
    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
      min-height: 100%;
      overflow: auto;
      padding: 80px 0 0;
    }
  }
`;

const AmountStep = (props) => {
  const {
    isLoading,
    type,
    externalLinkRoute,
    hasGroups,
    group,
    onSubmit,
    error,
    maxAmount,
    maxAmountWarning,
  } = props;

  const [amount, setAmount] = useState(0);
  const [byMonth, setByMonth] = useState(false);
  const [groupPercentage, setGroupPercentage] = useState();

  const hasGroup = !!group?.id;
  const hasSubmit = !isLoading && amount && amount <= maxAmount;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      amount,
      to: type,
      type: byMonth ? "M" : "S",
      allocations:
        hasGroup && groupPercentage
          ? [
              {
                group: group?.id,
                amount: (amount * groupPercentage) / 100,
              },
            ]
          : [],
    });
  };

  return (
    <Theme type={type}>
      <StyledPage>
        <StyledIllustration aria-hidden="true" />
        <StyledBody>
          <StyledMain>
            <StyledLogo
              alt={`Logo ${
                type === "2022" ? "Mélenchon 2022" : "la France insoumise"
              }`}
              route={externalLinkRoute}
              rel="noopener noreferrer"
              target="_blank"
            />
            {!hasGroup && hasGroups ? (
              <StyledGroupLink>
                <RawFeatherIcon name="share" />
                <span>
                  <strong>Pour faire un don alloué</strong> vers votre groupe
                  d'action certifié, utilisez le bouton "financer" dans{" "}
                  <Link route="groups">la page de votre groupe</Link>
                </span>
              </StyledGroupLink>
            ) : null}
            <h2>Faire un don</h2>
            {type !== "2022" ? (
              <h4>
                à la France insoumise (faire un don à{" "}
                <Link route="donations" routeParams={{ type: "2022" }}>
                  Mélenchon 2022
                </Link>
                &nbsp;?)
              </h4>
            ) : (
              <Spacer size="1rem" />
            )}
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
                  Chaque don nous aide à l’organisation d’événements, à l’achat
                  de matériel, au fonctionnement de ce site, etc.
                </p>
                <p>
                  Nous avons besoin du soutien financier de chacun·e d’entre
                  vous.
                </p>
              </>
            )}
            <form onSubmit={handleSubmit}>
              <AmountWidget
                disabled={isLoading}
                amount={amount}
                maxAmount={maxAmount}
                maxAmountWarning={maxAmountWarning}
                byMonth={byMonth}
                groupPercentage={hasGroup ? groupPercentage : undefined}
                onChangeAmount={setAmount}
                onChangeByMonth={setByMonth}
                onChangeGroupPercentage={
                  hasGroup ? setGroupPercentage : undefined
                }
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
            <LegalParagraph>
              {type === "2022"
                ? "Les dons sont destinés à l'AFCP JLM 2022, déclarée à la préfecture de Paris le 15 juin 2021, seule habilitée à recevoir les dons en faveur du candidat Jean-Luc Mélenchon, dans le cadre de la campagne pour l'élection présidentielle de 2022."
                : "Les dons seront versés à La France insoumise. Premier alinéa de l’article 11-4 de la loi 88-227 du 11 mars 1988 modifiée : une personne physique peut verser un don à un parti ou groupement politique si elle est de nationalité française ou si elle réside en France."}
            </LegalParagraph>
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
    </Theme>
  );
};

AmountStep.propTypes = {
  hasGroups: PropTypes.bool,
  group: PropTypes.object,
  type: PropTypes.oneOf(Object.keys(CONFIG)),
  externalLinkRoute: PropTypes.string,
  isLoading: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  error: PropTypes.string,
  maxAmount: PropTypes.number,
  maxAmountWarning: PropTypes.node,
};

export default AmountStep;
