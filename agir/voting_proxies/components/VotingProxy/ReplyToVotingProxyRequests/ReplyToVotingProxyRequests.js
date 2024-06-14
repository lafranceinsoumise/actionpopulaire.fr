import PropTypes from "prop-types";
import React from "react";
import { useLocation } from "react-router-dom";
import useSWRImmutable from "swr/immutable";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";

import ReplyingForm from "./ReplyingForm";
import NoRequestFound from "./NoRequestFound";

import { routeConfig } from "@agir/front/app/routes.config";
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

const ReplyToVotingProxyRequests = (props) => {
  const { votingProxyPk } = props;

  const { pathname, search } = useLocation();
  const isReadOnly = routeConfig.acceptedVotingProxyRequests.match(pathname);
  const votingProxyRequestsIds =
    getVotingProxyRequestsIdsFromURLSearchParams(search);
  const { data, error, mutate, isLoading } = useSWRImmutable(
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

  return (
    <StyledPageContainer theme={votingProxyTheme}>
      <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
        {error?.response?.status === 404 || data?.requests?.length === 0 ? (
          <NoRequestFound hasMatchedRequests={!!votingProxyRequestsIds} />
        ) : (
          data && (
            <ReplyingForm
              votingProxyPk={votingProxyPk}
              firstName={data.firstName}
              requests={data.requests}
              refreshRequests={mutate}
              readOnly={data.readOnly}
              hasMatchedRequests={!!votingProxyRequestsIds}
            />
          )
        )}
      </PageFadeIn>
    </StyledPageContainer>
  );
};
ReplyToVotingProxyRequests.propTypes = {
  votingProxyPk: PropTypes.string.isRequired,
};
export default ReplyToVotingProxyRequests;
