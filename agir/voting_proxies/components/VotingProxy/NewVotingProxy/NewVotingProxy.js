import React, { useCallback } from "react";
import useSWRImmutable from "swr/immutable";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import VotingProxyForm from "./VotingProxyForm";
import { WarningBlock } from "@agir/elections/Common/StyledComponents";
import { votingProxyTheme } from "@agir/voting_proxies/Common/themes";

const NewVotingProxy = () => {
  const { data: session, mutate } = useSWRImmutable("/api/session/");

  const handleSuccess = useCallback(
    (votingProxy) => {
      mutate({
        optimisticData: (session) => ({
          ...session,
          votingProxyPk: votingProxy.id,
        }),
      });
    },
    [mutate],
  );

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
        <VotingProxyForm user={session?.user} onSuccess={handleSuccess} />
      </PageFadeIn>
    </StyledPageContainer>
  );
};

export default NewVotingProxy;
