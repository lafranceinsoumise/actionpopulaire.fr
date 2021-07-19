import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Modal from "@agir/front/genericComponents/Modal";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import Toast from "@agir/front/genericComponents/Toast";

import MissingDocumentList from "./MissingDocumentList";

const CloseButton = styled.button``;

const StyledModalContent = styled.div`
  max-width: 716px;
  position: relative;
  width: 100%;
  padding: 3rem;
  margin: 60px auto 0;
  box-shadow: ${(props) => props.theme.elaborateShadow};
  background-color: ${(props) => props.theme.white};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
    padding: 1.5rem;
    border-radius: 0;
    margin: 0;
    min-height: 100%;
  }

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

  ${CloseButton} {
    position: absolute;
    top: 3rem;
    right: 3rem;
    padding: 0;
    color: ${(props) => props.theme.black1000};
    z-index: 1;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      top: 1.5rem;
      right: 1.5rem;
    }
  }

  ${Toast} {
    width: 100%;
  }
`;

export const MissingDocumentModal = (props) => {
  const { shouldShow, onClose, projects, isBlocked } = props;

  return (
    <Modal shouldShow={shouldShow} onClose={onClose} noScroll>
      <StyledModalContent>
        <CloseButton onClick={onClose} aria-label="Fermer la modale">
          <RawFeatherIcon name="x" width="1.5rem" height="1.5rem" />
        </CloseButton>
        <header>
          <h3>Mes documents justificatifs</h3>
          {isBlocked && (
            <Toast style={{ display: "block", margin: " 0 0 1.5rem" }}>
              <strong>
                Action requise : vous avez des documents en attente.
              </strong>
              <br />
              Tant que vous n’aurez pas envoyé ces documents (ou indiqué qu’ils
              ne sont pas nécessaires), vous ne pourrez plus créer d’événement
              public.
            </Toast>
          )}
          <p>
            <strong>
              Pour chaque événement public visant à susciter des
              suffrages&nbsp;:
            </strong>{" "}
            envoyez des documents justifiant que vous n’avez engagé aucun frais
            personnel.{" "}
            <a href="https://infos.actionpopulaire.fr">En savoir plus</a>
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
      </StyledModalContent>
    </Modal>
  );
};

MissingDocumentModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
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
