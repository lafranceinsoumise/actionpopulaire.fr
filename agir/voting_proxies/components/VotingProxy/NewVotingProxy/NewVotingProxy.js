import React from "react";
import useSWR from "swr";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import VotingProxyForm from "./VotingProxyForm";

import { votingProxyTheme } from "@agir/voting_proxies/Common/themes";

const NewVotingProxy = () => {
  const { data: session } = useSWR("/api/session/");

  return (
    <StyledPageContainer theme={votingProxyTheme}>
      <PageFadeIn
        ready={typeof session !== "undefined"}
        wait={
          <>
            <Spacer size="1rem" />
            <Skeleton />
          </>
        }
      >
        <VotingProxyForm user={session?.user} />
      </PageFadeIn>
    </StyledPageContainer>
  );
};

export default NewVotingProxy;
