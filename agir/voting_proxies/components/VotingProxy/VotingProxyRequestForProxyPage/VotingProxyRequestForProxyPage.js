import React from "react";
import useSWRImmutable from "swr/immutable";

import { MailTo } from "@agir/elections/Common/StyledComponents";
import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import AppRedirect from "@agir/front/app/Redirect";
import Button from "@agir/front/genericComponents/Button";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import RequestCard from "./RequestCard";
import { WarningBlock } from "@agir/elections/Common/StyledComponents";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { getVotingProxyEndpoint } from "@agir/voting_proxies/Common/api";
import { votingProxyTheme } from "@agir/voting_proxies/Common/themes";

const VotingProxyRequestForProxyPage = ({ votingProxyPk }) => {
  const isDesktop = useIsDesktop();

  const {
    data: votingProxy,
    error,
    isLoading,
  } = useSWRImmutable(
    votingProxyPk &&
      getVotingProxyEndpoint("votingProxyRequestsForProxy", {
        votingProxyPk,
      }),
  );

  if (error?.response?.status === 404 || votingProxy?.requests.length === 0) {
    return (
      <AppRedirect
        route="replyToVotingProxyRequests"
        routeParams={{ votingProxyPk }}
      />
    );
  }

  return (
    <StyledPageContainer theme={votingProxyTheme}>
      <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
        {!isLoading && (
          <>
            <div>
              <h2>Propositions de procurations de vote</h2>
              <Spacer size="0.5rem" />
              <p>
                Retrouvez ci-dessous les demandes en attente près de l'adresse
                que vous avez indiquée lors de votre inscription :
              </p>
              <Spacer size="1rem" />
              <WarningBlock
                icon="alert-triangle"
                style={{ fontSize: "0.875rem" }}
              >
                <strong>Attention !</strong> Les liens ci-dessous sont
                personnalisés pour vous et{" "}
                <strong>
                  ne peuvent pas être transférés à d'autres volontaires
                </strong>
                . Si vous connaissez d'autres personnes qui pourraient prendre
                des procurations, n'hesitez pas à leur dire de s'inscrire !
              </WarningBlock>
              <Spacer size="1.5rem" />
              <div
                css={`
                  display: grid;
                  gap: 1rem;
                `}
              >
                {votingProxy?.requests.map((request) => (
                  <RequestCard key={request.replyURL} {...request} />
                ))}
              </div>
              <Spacer size="1.5rem" />
              <footer style={{ textAlign: "center" }}>
                <Button
                  link
                  block
                  icon="arrow-left"
                  route="replyToVotingProxyRequests"
                  routeParams={{ votingProxyPk }}
                >
                  Retour
                </Button>
              </footer>
              <Spacer size="1.5rem" />
              <MailTo />
            </div>
          </>
        )}
      </PageFadeIn>
    </StyledPageContainer>
  );
};

export default VotingProxyRequestForProxyPage;
