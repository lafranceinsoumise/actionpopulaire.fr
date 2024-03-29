import PropTypes from "prop-types";
import React from "react";
import { useLocation } from "react-router-dom";
import useSWR from "swr";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";

import ReplyingForm from "./ReplyingForm";
import NoRequestFound from "./NoRequestFound";

import { routeConfig } from "@agir/front/app/routes.config";
import { getVotingProxyEndpoint } from "@agir/voting_proxies/Common/api";

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

const ReplyToVotingProxyRequests = (props) => {
  const { votingProxyPk } = props;

  const { pathname, search } = useLocation();
  const isReadOnly = routeConfig.acceptedVotingProxyRequests.match(pathname);
  const votingProxyRequestsIds =
    getVotingProxyRequestsIdsFromURLSearchParams(search);
  const { data, error, mutate } = useSWR(
    getVotingProxyEndpoint(
      "replyToVotingProxyRequests",
      { votingProxyPk },
      { vpr: votingProxyRequestsIds || undefined, ro: isReadOnly ? "1" : "0" },
    ),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );

  if (error?.response?.status === 404) {
    // The voting proxy does not exist or is no longer available
    return <NotFoundPage hasTopBar={false} reloadOnReconnection={false} />;
  }

  return (
    <StyledPageContainer>
      <PageFadeIn ready={typeof data !== "undefined"} wait={<Skeleton />}>
        {data && data.requests.length > 0 ? (
          <ReplyingForm
            votingProxyPk={votingProxyPk}
            firstName={data.firstName}
            requests={data.requests}
            refreshRequests={mutate}
            readOnly={data.readOnly}
            hasMatchedRequests={!!votingProxyRequestsIds}
          />
        ) : (
          <NoRequestFound hasMatchedRequests={!!votingProxyRequestsIds} />
        )}
      </PageFadeIn>
    </StyledPageContainer>
  );
};
ReplyToVotingProxyRequests.propTypes = {
  votingProxyPk: PropTypes.string.isRequired,
};
export default ReplyToVotingProxyRequests;
