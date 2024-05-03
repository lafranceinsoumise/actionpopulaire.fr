import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";

import JoinAGroupCard from "./JoinAGroupCard";
import ActionTools from "./ActionTools";
import DonateCard from "./DonateCard";
import CanvassCard from "@agir/events/Canvass/CanvassCard";
import TokTokCard from "@agir/events/TokTok/TokTokCard";

const StyledButtons = styled.div`
  display: flex;
  gap: 0.5rem;

  ${Button} {
    flex: 1 1 50%;
  }
`;

const MainContainer = styled.div`
  width: 100%;
  max-width: 1442px;
  margin: 0 auto;
  padding: 0 50px 3rem;
  display: flex;
  gap: 2.5rem;

  h2 {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.4;
    margin: 2rem 0 1rem;

    small {
      font-size: 0.813rem;
      color: ${(props) => props.theme.redNSP};
      text-transform: uppercase;
    }
  }

  aside {
    flex: 0 0 373px;
  }

  main {
    flex: 1 1 100%;
  }
`;

const DesktopActionToolsPage = (props) => {
  const { firstName, donationAmount, hasGroups, city, commune } = props;

  return (
    <MainContainer>
      <main>
        <h2>Méthodes d'action</h2>
        <ActionTools />
      </main>
      <aside>
        <h2>Besoin d'aide&nbsp;?</h2>
        <StyledButtons>
          <Button link route="help">
            Centre d'aide
          </Button>
          <Button link route="contact">
            Nous contacter
          </Button>
        </StyledButtons>
        <h2>Outils de porte-à-porte</h2>
        <CanvassCard />
        <Spacer size="1rem" />
        <TokTokCard />
        <PageFadeIn ready={typeof hasGroups !== "undefined"}>
          {!hasGroups && (
            <>
              <h2>Conseillé pour {firstName || "vous"}</h2>
              <JoinAGroupCard city={city} commune={commune} />
            </>
          )}
        </PageFadeIn>
        <PageFadeIn ready={typeof donationAmount !== "undefined"}>
          {donationAmount && (
            <>
              <h2>Financer la campagne</h2>
              <DonateCard amount={donationAmount} />
            </>
          )}
        </PageFadeIn>
      </aside>
    </MainContainer>
  );
};
DesktopActionToolsPage.propTypes = {
  firstName: PropTypes.string,
  donationAmount: PropTypes.number,
  hasGroups: PropTypes.bool,
  city: PropTypes.string,
  commune: PropTypes.object,
};
export default DesktopActionToolsPage;
