import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";
import useSWRImmutable from "swr/immutable";

import * as api from "@agir/donations/spendingRequest/common/api";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import AppRedirect from "@agir/front/app/Redirect";
import SpendingRequestHistory from "./SpendingRequestHistory";

const StyledPage = styled.main`
  padding: 2rem;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;

  nav {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin: 0 0 1.25rem;
      flex-flow: column-reverse nowrap;
      justify-content: space-between;
    }

    & > * {
      flex: 0 0 auto;
    }

    h2 {
      font-size: 1.625rem;
      font-weight: 700;
      margin: 0;
      margin-right: auto;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        font-size: 1.375rem;
      }
    }

    div {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-left: auto;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        gap: 0.5rem;
      }
    }
  }
`;

const SpendingRequestHistoryPage = ({ spendingRequestPk }) => {
  const { data: _session, isLoading: isSessionLoading } =
    useSWRImmutable("/api/session/");

  const { data: spendingRequest, isLoading: isSpendingRequestLoading } = useSWR(
    api.getSpendingRequestEndpoint("getSpendingRequest", {
      spendingRequestPk,
    }),
  );

  const isDesktop = useIsDesktop();
  const isReady = !isSpendingRequestLoading && !isSessionLoading;

  if (isDesktop) {
    return (
      <AppRedirect
        route="spendingRequestDetails"
        routeParams={{ spendingRequestPk }}
      />
    );
  }

  return (
    <PageFadeIn ready={isReady} wait={<Skeleton />}>
      {isReady && spendingRequest && (
        <StyledPage>
          <SpendingRequestHistory history={spendingRequest.history} />
        </StyledPage>
      )}
    </PageFadeIn>
  );
};

SpendingRequestHistoryPage.propTypes = {
  spendingRequestPk: PropTypes.string,
};

export default SpendingRequestHistoryPage;
