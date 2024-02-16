import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import hrefs from "@agir/front/globalContext/nonReactRoutes.config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";

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

  ${StaticToast} {
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
          <StaticToast style={{ display: "block", margin: " 0 0 1.5rem" }}>
            <strong>
              Action requise : vous avez des documents en attente.
            </strong>
            <br />
            Tant que vous n’aurez pas envoyé ces documents (ou indiqué qu’ils ne
            sont pas nécessaires), vous ne pourrez plus créer d’événement
            public.
          </StaticToast>
        )}
        <p>
          <strong>
            Pour chaque événement public visant à susciter des suffrages
          </strong>{" "}
          envoyez des documents justifiant que vous n’avez engagé aucun frais
          personnel.
        </p>
        <Spacer size="1.5rem" />
        <p>
          Les informations relatives aux documents des événements suivants sont
          toujours en attente d'être complétées :
        </p>
      </header>
      <Spacer size="1.5rem" />
      <PageFadeIn ready={Array.isArray(projects)}>
        {projects && projects.length > 0 ? (
          <MissingDocumentList projects={projects} />
        ) : (
          <StaticToast $color="#16A460" style={{ margin: 0, fontWeight: 500 }}>
            <RawFeatherIcon name="check" strokeWidth={2} />
            &ensp;Vous êtes à jour de vos documents à envoyer&nbsp;!
          </StaticToast>
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
    }),
  ),
  isBlocked: PropTypes.bool,
};

export default MissingDocumentModal;
