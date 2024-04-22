import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { useLocation } from "react-router-dom";
import useSWRImmutable from "swr/immutable";

import AppRedirect from "@agir/front/app/Redirect";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";

import NoRequestFound from "./NoRequestFound";
import ReplyingForm from "./ReplyingForm";

import { getVotingProxyEndpoint } from "@agir/voting_proxies/Common/api";
import { votingProxyTheme } from "@agir/voting_proxies/Common/themes";

const getVotingProxyRequestsIdsFromURLSearchParams = (search) => {
  if (!search) {
    return null;
  }
  const searchParams = new URLSearchParams(search);
  const ids = searchParams.get("vpr");

  if (!ids) {
    return null;
  }

  return ids;
};

const ReplyToSingleVotingProxyRequest = (props) => {
  const { votingProxyRequestPk } = props;

  const location = useLocation();

  const { data: session, isLoading: sessionIsLoading } = useSWRImmutable(
    "/api/session/",
    { revalidateOnMount: true },
  );

  const votingProxyPk = useMemo(() => {
    if (location.state?.votingProxyId) {
      return location.state.votingProxyId;
    }

    if (location.search) {
      return new URLSearchParams(location.search).get("vp");
    }

    return session?.user.votingProxyId || null;
  }, [location.state, location.search, session]);

  const { data: votingProxy, isLoading: votingProxyIsLoading } =
    useSWRImmutable(
      votingProxyPk &&
        getVotingProxyEndpoint("retrieveUpdateVotingProxy", { votingProxyPk }),
    );

  const {
    data: votingProxyRequest,
    error,
    isLoading: votingProxyRequestIsLoading,
  } = useSWRImmutable(
    votingProxy?.isAvailable &&
      getVotingProxyEndpoint(
        "retrieveUpdateVotingProxyRequest",
        { votingProxyRequestPk },
        { votingProxyPk },
      ),
  );

  const isLoading =
    sessionIsLoading || votingProxyIsLoading || votingProxyRequestIsLoading;

  if (!votingProxyPk || votingProxy?.status === "unavailable") {
    return (
      <AppRedirect
        route="newVotingProxy"
        state={{
          next: location.pathname,
        }}
        toast={[
          "Vous devez vous inscrire en tant que volontaire avant de pouvoir accepter de procurations de vote",
          "WARNING",
        ]}
      />
    );
  }

  if (votingProxy?.isAvailable === false) {
    return (
      <AppRedirect
        route="acceptedVotingProxyRequests"
        routeParams={{ votingProxyPk }}
        toast={[
          "Vous ne pouvez plus accepter d'autres demandes de procurations",
          "WARNING",
        ]}
      />
    );
  }

  if (error?.response?.status === 404) {
    // The voting proxy request does not exist or is no longer pending
    return <NotFoundPage hasTopBar={false} reloadOnReconnection={false} />;
  }

  return (
    <StyledPageContainer theme={votingProxyTheme}>
      <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
        {error?.response?.status === 403 || !votingProxyRequest ? (
          <NoRequestFound
            votingProxyPk={votingProxyPk}
            hasMatchedRequests
            hasMatchingLink
          />
        ) : (
          <ReplyingForm
            votingProxyPk={votingProxyPk}
            firstName={votingProxy?.firstName}
            singleRequest={votingProxyRequest}
            hasMatchedRequests
          />
        )}
      </PageFadeIn>
    </StyledPageContainer>
  );
};
ReplyToSingleVotingProxyRequest.propTypes = {
  votingProxyRequestPk: PropTypes.string.isRequired,
};
export default ReplyToSingleVotingProxyRequest;
