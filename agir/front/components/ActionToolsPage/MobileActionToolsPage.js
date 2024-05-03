import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import BottomBar from "@agir/front/app/Navigation/BottomBar";
import Button from "@agir/front/genericComponents/Button";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import RenderIfVisible from "@agir/front/genericComponents/RenderIfVisible";

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

const StyledPage = styled.main`
  padding: 1rem 1rem 5.5rem;

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
`;

const MobileActionToolsPage = (props) => {
  const { firstName, donationAmount, hasGroups, city, commune } = props;

  return (
    <>
      <StyledPage>
        <StyledButtons>
          <Button link route="help">
            Centre d'aide
          </Button>
          <Button link route="contact">
            Nous contacter
          </Button>
        </StyledButtons>
        <PageFadeIn ready={typeof hasGroups !== "undefined"}>
          {!hasGroups && (
            <>
              <h2>Conseillé pour {firstName || "vous"}</h2>
              <JoinAGroupCard city={city} commune={commune} />
            </>
          )}
        </PageFadeIn>
        <h2>Méthodes d'action</h2>
        <ActionTools />
        <h2>Outils de porte-à-porte</h2>
        <CanvassCard />
        <Spacer size="1rem" />
        <TokTokCard />
        <PageFadeIn ready={typeof donationAmount !== "undefined"}>
          {donationAmount && (
            <RenderIfVisible offset={0}>
              <h2>Financer la campagne</h2>
              <DonateCard amount={donationAmount} />
            </RenderIfVisible>
          )}
        </PageFadeIn>
      </StyledPage>
      <BottomBar active="actionTools" />
    </>
  );
};
MobileActionToolsPage.propTypes = {
  firstName: PropTypes.string,
  donationAmount: PropTypes.number,
  hasGroups: PropTypes.bool,
  city: PropTypes.string,
  commune: PropTypes.object,
};
export default MobileActionToolsPage;
