import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";
import useSWRImmutable from "swr/immutable";

import { Button } from "@agir/donations/common/StyledComponents";
import BackLink from "@agir/front/app/Navigation/BackLink";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { getGroupEndpoint } from "@agir/groups/utils/api";
import SpendingRequestForm from "./SpendingRequestForm";

const StyledPage = styled.main`
  padding: 2rem;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;

  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;

    & > * {
      margin: 0;
    }

    strong {
      font-weight: inherit;
      text-decoration: underline;
    }

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    margin: 2rem 0 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.375rem;
      margin: 0 0 1.25rem;
    }
  }
`;

const CreateSpendingRequestPage = ({ groupPk }) => {
  const { data: session, isLoading: isSessionLoading } =
    useSWRImmutable("/api/session/");

  const { data: group, isLoading: isGroupLoading } = useSWRImmutable([
    getGroupEndpoint("getGroup", { groupPk }),
  ]);

  const { data: finance, isLoading: isFinanceLoading } = useSWRImmutable([
    getGroupEndpoint("getFinance", { groupPk }),
  ]);

  const availableAmount = useMemo(
    () => (finance?.donation ? finance.donation : 0),
    [finance]
  );

  const isReady = !isFinanceLoading && !isGroupLoading && !isSessionLoading;

  return (
    <PageFadeIn ready={isReady} wait={<Skeleton />}>
      {isReady && (
        <StyledPage>
          <nav>
            <BackLink />
            <Button
              link
              color="link"
              icon="arrow-right"
              route="spendingRequestHelp"
            >
              Un doute ? Consultez le <strong>centre d'aide</strong>
            </Button>
          </nav>
          <h2>Nouvelle dépense</h2>
          <SpendingRequestForm
            user={session?.user}
            group={group}
            availableAmount={availableAmount}
          />
        </StyledPage>
      )}
    </PageFadeIn>
  );
};

CreateSpendingRequestPage.propTypes = {
  groupPk: PropTypes.string,
};

export default CreateSpendingRequestPage;
