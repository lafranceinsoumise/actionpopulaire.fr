import React from "react";
import useSWR from "swr";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/voting_proxies/Common/StyledPageContainer";
import VotingProxyForm from "./VotingProxyForm";

const NewVotingProxy = (props) => {
  const { data: session } = useSWR("/api/session/");

  return (
    <StyledPageContainer>
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
