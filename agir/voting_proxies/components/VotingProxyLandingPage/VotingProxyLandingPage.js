import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import ElectionDayWarningBlock from "@agir/voting_proxies/Common/ElectionDayWarningBlock";

import votingProxyRequestIcon from "@agir/voting_proxies/Common/images/vpr_icon.png";
import votingProxyIcon from "@agir/voting_proxies/Common/images/vp_icon.png";

const StyledLink = styled(Card).attrs({ bordered: true })`
  display: flex;
  align-items: center;
  padding: 1.5rem;
  font-size: 0.875rem;
  gap: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
    text-align: center;
  }

  & > p {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;
    margin: 0;
    gap: 1rem;

    strong {
      font-size: 1.375rem;
      font-weight: 700;
    }

    ${Button} {
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.2;

      &,
      &:hover,
      &:focus {
        text-decoration: none;
      }
    }
  }

  & > img {
    flex: 1 1 auto;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      width: 104px;
      height: auto;
    }
  }
`;

const VotingProxyLandingPage = () => {
  const isDesktop = useIsDesktop();

  return (
    <StyledPageContainer>
      <h2 style={{ fontSize: "1.75rem", textAlign: "center" }}>
        Espace Procurations
      </h2>
      <Spacer size={isDesktop ? "2.5rem" : "1rem"} />
      <ElectionDayWarningBlock />
      <Spacer size="1rem" />
      <StyledLink>
        <img src={votingProxyRequestIcon} width="143" height="132" />
        <p>
          <strong>Je serai absent·e le 9 juin</strong>
          <Button
            link
            wrap
            color="default"
            icon={isDesktop ? "arrow-right" : undefined}
            route="newVotingProxyRequest"
          >
            Faire une procuration pour que quelqu'un vote à ma place
          </Button>
        </p>
      </StyledLink>
      <Spacer size="1rem" />
      <StyledLink>
        <img src={votingProxyIcon} width="143" height="132" />
        <p>
          <strong>Je suis volontaire</strong>
          <Button
            link
            wrap
            color="default"
            icon={isDesktop ? "arrow-right" : undefined}
            route="newVotingProxy"
          >
            Prendre une procuration pour voter à la place de quelqu'un
          </Button>
        </p>
      </StyledLink>
      <Spacer size={isDesktop ? "8rem" : "2rem"} />
      <footer style={{ textAlign: "center" }}>
        <Button color="dismiss" icon="arrow-right" link route="eu2024">
          Retourner sur le site
        </Button>
      </footer>
    </StyledPageContainer>
  );
};

export default VotingProxyLandingPage;
