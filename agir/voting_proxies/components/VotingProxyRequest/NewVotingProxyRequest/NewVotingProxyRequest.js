import React from "react";
import useSWR from "swr";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import VotingProxyRequestForm from "./VotingProxyRequestForm";

import { votingProxyRequestTheme } from "@agir/voting_proxies/Common/themes";

const NewVotingProxyRequest = () => {
  const { data: session } = useSWR("/api/session/");

  return (
    <StyledPageContainer theme={votingProxyRequestTheme}>
      <PageFadeIn
        ready={typeof session !== "undefined"}
        wait={
          <>
            <Spacer size="1rem" />
            <Skeleton />
          </>
        }
      >
        <VotingProxyRequestForm user={session?.user} />
      </PageFadeIn>
    </StyledPageContainer>
  );
};

export default NewVotingProxyRequest;
