import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";
import useSWR from "swr";
import useSWRImmutable from "swr/immutable";

import { Button } from "@agir/donations/common/StyledComponents";
import BackLink from "@agir/front/app/Navigation/BackLink";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { getGroupEndpoint } from "@agir/groups/utils/api";
import EditSpendingRequestForm from "./EditSpendingRequestForm";

import { getSpendingRequestEndpoint } from "@agir/donations/spendingRequest/common/api";

const StyledPage = styled.main`
  padding: 2rem;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1.5rem;
    max-width: 100%;
    min-height: calc(100vh - 300px);
  }

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

const EditSpendingRequestPage = ({ spendingRequestPk }) => {
  const { data: _session, isLoading: isSessionLoading } =
    useSWRImmutable("/api/session/");

  const {
    data: spendingRequest,
    isLoading: isSpendingRequestLoading,
    mutate,
  } = useSWR(
    getSpendingRequestEndpoint("getSpendingRequest", {
      spendingRequestPk,
    }),
  );

  const { data: finance, isLoading: isFinanceLoading } = useSWRImmutable([
    spendingRequest &&
      getGroupEndpoint("getFinance", { groupPk: spendingRequest.group.id }),
  ]);

  const availableAmount = useMemo(
    () => (finance?.donation ? finance.donation : 0),
    [finance],
  );

  const isReady =
    !isSessionLoading && !isSpendingRequestLoading && !isFinanceLoading;

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
          <h2>Modification de la demande</h2>
          <EditSpendingRequestForm
            spendingRequest={spendingRequest}
            availableAmount={availableAmount}
            onUpdate={mutate}
          />
        </StyledPage>
      )}
    </PageFadeIn>
  );
};

EditSpendingRequestPage.propTypes = {
  spendingRequestPk: PropTypes.string,
};

export default EditSpendingRequestPage;
