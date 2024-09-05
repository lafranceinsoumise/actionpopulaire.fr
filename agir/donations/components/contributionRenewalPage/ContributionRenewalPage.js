import countries from "localized-countries/data/fr";
import { DateTime } from "luxon";
import React, { useMemo } from "react";
import styled from "styled-components";

import {
  GENDER_OPTIONS,
  MONTHLY_PAYMENT,
} from "@agir/donations/common/form.config";
import { useContributionRenewal } from "@agir/donations/common/hooks";
import { displayPrice } from "@agir/lib/utils/display";

import AllocationDetails, {
  InactiveGroupAllocation,
} from "@agir/donations/common/AllocationDetails";
import {
  Button,
  StyledBody,
  StyledLogo,
  StyledMain,
  StyledPage,
  Theme,
} from "@agir/donations/common/StyledComponents";
import AppRedirect from "@agir/front/app/Redirect";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";

const StyledAmount = styled.div`
  font-size: 2rem;
  line-height: 1.5;
  font-weight: 400;

  small {
    font-size: 1rem;
    line-height: 1.6;
  }
`;
const StyledAllocations = styled.div``;
const StyledPaymentTiming = styled.div``;
const StyledEndDate = styled.div``;
const StyledPersonalInformation = styled.div`
  display: flex;
  flex-flow: column nowrap;
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid ${(props) => props.theme.text100};

  p {
    margin: 0;
    font-size: 0.875rem;

    strong {
      font-size: 1rem;
      font-weight: 600;
    }
  }
`;

const StyledContent = styled.div`
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;
  padding-bottom: 4rem;

  & > * {
    margin: 0;
  }

  h4 {
    font-size: 1.125rem;
    font-weight: 700;
    line-height: 1.419;
    margin: 0;
  }

  h6 {
    font-size: 0.875rem;
    font-weight: 600;
    line-height: 1.5;
    margin: 0 0 -0.5rem;
  }

  & > p strong {
    font-weight: 600;

    u {
      text-decoration: none;
      border-bottom: 4px solid ${(props) => props.theme.primary150};
    }
  }

  ${StyledAmount},
  ${StyledPaymentTiming},
  ${StyledEndDate} {
    display: flex;
    flex-flow: row nowrap;
    gap: 1rem;
    align-items: center;
    border-radius: ${(props) => props.theme.borderRadius};
    border: 1px solid ${(props) => props.theme.text100};
    padding: 1rem;
  }

  footer {
    display: flex;
    flex-flow: row wrap;
    gap: 1rem;
    align-items: center;

    & > * {
      flex: 1 0 auto;
    }
  }
`;

const ContributionPage = () => {
  const {
    config,
    activeContribution,
    endDate,
    allocations,
    inactiveGroupAllocation,
    group,
    errors,
    isReady,
    isLoading,
    onSubmit,
  } = useContributionRenewal();

  const isMonthly = activeContribution?.paymentTiming === MONTHLY_PAYMENT;

  const gender = useMemo(() => {
    if (!activeContribution) {
      return "";
    }

    const gender = GENDER_OPTIONS.find(
      (option) => option.value === activeContribution.gender,
    );
    return gender.label;
  }, [activeContribution]);

  const fullName = useMemo(() => {
    if (!activeContribution) {
      return "";
    }

    return [
      activeContribution.firstName,
      activeContribution.lastName.toUpperCase(),
    ]
      .filter(Boolean)
      .join(" ");
  }, [activeContribution]);

  const nationality = useMemo(
    () =>
      activeContribution?.nationality
        ? countries[activeContribution.nationality] ||
          activeContribution.nationality
        : "",
    [activeContribution],
  );

  const address = useMemo(() => {
    if (!activeContribution) {
      return "";
    }
    const {
      locationAddress1,
      locationAddress2,
      locationZip,
      locationCity,
      locationCountry,
    } = activeContribution;

    return [
      locationAddress1,
      locationAddress2,
      `${locationZip} ${locationCity}`.trim(),
      countries[locationCountry] || locationCountry,
    ]
      .filter(Boolean)
      .join(", ");
  }, [activeContribution]);

  const endDateString = useMemo(
    () =>
      activeContribution?.endDate
        ? DateTime.fromJSDate(new Date(activeContribution.endDate))
            .setLocale("fr")
            .toFormat("dd MMMM yyyy")
        : "",
    [activeContribution],
  );

  const newEndDateString = useMemo(
    () =>
      DateTime.fromJSDate(new Date(endDate))
        .setLocale("fr")
        .toFormat("dd MMMM yyyy"),
    [endDate],
  );

  if (isReady && !activeContribution) {
    return <AppRedirect route="contributions" />;
  }

  if (isReady && !activeContribution.renewable) {
    return <AppRedirect route="alreadyContributor" />;
  }

  return (
    <Theme type={activeContribution?.to} theme={config.theme}>
      <StyledPage
        css={`
          overflow: auto;
          height: auto;

          ${StyledBody} {
            padding-top: 2rem;
          }
        `}
      >
        <StyledBody>
          <PageFadeIn
            ready={isReady && !!activeContribution}
            wait={
              <StyledMain>
                <Skeleton boxes="4" />
              </StyledMain>
            }
          >
            {activeContribution && (
              <StyledMain>
                <StyledLogo
                  alt={`Logo ${config.beneficiary}`}
                  route={config.externalLinkRoute}
                  rel="noopener noreferrer"
                  target="_blank"
                />
                <StyledContent>
                  <h2>Renouveler mon financement à la France insoumise</h2>
                  <Spacer size="0" />
                  <h4>À l’heure actuelle, votre financement est de&nbsp;:</h4>
                  <StyledAmount>
                    {displayPrice(activeContribution.amount, true)
                      .split(" ")
                      .map((element) => (
                        <span key={element}>{element}</span>
                      ))}
                    <small>par mois</small>
                  </StyledAmount>
                  {allocations.length > 0 && (
                    <>
                      <h4>Réparti de la manière suivante :</h4>
                      <InactiveGroupAllocation
                        allocation={inactiveGroupAllocation}
                        byMonth={isMonthly}
                      />
                      <StyledAllocations>
                        <AllocationDetails
                          allocations={allocations}
                          groupName={group?.name}
                          byMonth
                        />
                      </StyledAllocations>
                    </>
                  )}
                  <h4>Payé par&nbsp;:</h4>
                  <StyledPaymentTiming>
                    <FaIcon
                      icon={
                        isMonthly ? "credit-card" : "money-check-pen:regular"
                      }
                      size="1.5rem"
                    />
                    <strong>
                      {isMonthly
                        ? "Carte bancaire, une fois par mois"
                        : "Chèque, en une seule fois"}
                    </strong>
                  </StyledPaymentTiming>
                  <h6>Valable jusqu'au&nbsp;:</h6>
                  <StyledEndDate>{endDateString}</StyledEndDate>
                  <h6>Vos coordonnées :</h6>
                  <StyledPersonalInformation>
                    <p>
                      <strong>
                        {gender} {fullName}
                      </strong>
                    </p>
                    <p>
                      Nationalité&ensp;<strong>{nationality}</strong>
                    </p>
                    <p>
                      Adresse&ensp;<strong>{address}</strong>
                    </p>
                    <p>
                      Téléphone&ensp;
                      <strong>{activeContribution?.contactPhone}</strong>
                    </p>
                  </StyledPersonalInformation>
                  <Spacer size="0.5rem" />
                  <p>
                    <strong>
                      Vous pouvez choisir d’arrêter votre financement, de
                      changer certaines informations comme le montant, la
                      répartition ou vos coordonnées, ou bien le renouveler tel
                      quel <u>jusqu'au {newEndDateString}</u>.
                    </strong>
                  </p>
                  <Spacer size="0" />
                  {errors &&
                    !!Object.values(errors).filter((error) => !!error)
                      .length && (
                      <StaticToast>
                        {errors?.global || (
                          <>
                            Une erreur est survenue lors du renouvèlement de
                            votre contribution. Veuillez ressayer ou cliquer sur
                            le bouton &laquo; Modifier &raquo; pour vérifier les
                            informations enregistrées.
                          </>
                        )}
                      </StaticToast>
                    )}
                  <Spacer size="0" />
                  <footer>
                    <Button
                      link
                      color="choose"
                      route="personalPayments"
                      disabled={isLoading}
                    >
                      Ne pas renouveler
                    </Button>
                    <Button
                      link
                      color="secondary"
                      icon="edit-2"
                      route="contributions"
                      params={group ? { group: group.id } : undefined}
                      disabled={isLoading}
                    >
                      Modifier
                    </Button>
                    <Button
                      color="primary"
                      icon="refresh-cw"
                      onClick={onSubmit}
                      loading={isLoading}
                      disabled={isLoading}
                    >
                      Renouveler
                    </Button>
                  </footer>
                </StyledContent>
              </StyledMain>
            )}
          </PageFadeIn>
        </StyledBody>
      </StyledPage>
    </Theme>
  );
};

export default ContributionPage;
