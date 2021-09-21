import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import hrefs from "@agir/front/globalContext/nonReactRoutes.config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import Toast from "@agir/front/genericComponents/Toast";

import MissingDocumentList from "./MissingDocumentList";

const StyledContent = styled.div`
  header {
    h3 {
      padding: 0;
      margin: 0 0 1rem;
      font-weight: 700;
      font-size: 1.625rem;
      line-height: 1.5;
      max-width: calc(100% - 3rem);
    }

    p {
      margin: 0;

      strong {
        font-weight: 600;
      }
    }
  }

  ${Toast} {
    width: 100%;
  }
`;

export const MissingDocumentModal = (props) => {
  const { projects, isBlocked } = props;

  return (
    <StyledContent>
      <header>
        <h3>Mes documents justificatifs</h3>
        {isBlocked && (
          <Toast style={{ display: "block", margin: " 0 0 1.5rem" }}>
            <strong>
              Action requise : vous avez des documents en attente.
            </strong>
            <br />
            Tant que vous n’aurez pas envoyé ces documents (ou indiqué qu’ils ne
            sont pas nécessaires), vous ne pourrez plus créer d’événement
            public.
          </Toast>
        )}
        <p>
          <strong>
            Pour chaque événement public visant à susciter des suffrages&nbsp;:
          </strong>{" "}
          envoyez des documents justifiant que vous n’avez engagé aucun frais
          personnel.{" "}
          <a href={hrefs.campaignFundingHelp}>En savoir plus</a>
        </p>
        <Spacer size="0.5rem" />
        <p>
          <strong>Attention&nbsp;:</strong> vous ne pourrez plus créer
          d’événement public si vous en avez un de plus de 15 jours ayant des
          documents manquants.
        </p>
      </header>
      <Spacer size="1.5rem" />
      <PageFadeIn ready={Array.isArray(projects)}>
        {projects && projects.length > 0 ? (
          <MissingDocumentList projects={projects} />
        ) : (
          <Toast $color="#16A460" style={{ margin: 0, fontWeight: 500 }}>
            <RawFeatherIcon name="check" strokeWidth={2} />
            &ensp;Vous êtes à jour de vos documents à envoyer&nbsp;!
          </Toast>
        )}
      </PageFadeIn>
    </StyledContent>
  );
};

MissingDocumentModal.propTypes = {
  projects: PropTypes.arrayOf(
    PropTypes.shape({
      event: PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        endTime: PropTypes.string.isRequired,
      }),
      projectId: PropTypes.number.isRequired,
      missingDocumentCount: PropTypes.number.isRequired,
      limitDate: PropTypes.string.isRequired,
    })
  ),
  isBlocked: PropTypes.bool,
};

export default MissingDocumentModal;
