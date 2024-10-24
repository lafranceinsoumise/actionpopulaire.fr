import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Spacer from "@agir/front/genericComponents/Spacer";

import * as api from "@agir/events/common/api";
import { mutate } from "swr";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

const StyledDialog = styled.div`
  max-width: 540px;
  margin: 160px auto;
  background-color: ${(props) => props.theme.background0};
  border-radius: ${(props) => props.theme.borderRadius};
  padding: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0;
    border-radius: 0;
    max-width: 100%;
  }

  main {
    h4 {
      margin-top: 0;
      margin-bottom: 1rem;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.5;
    }

    p {
      margin: 0;
      padding: 0;
      font-size: 0.875rem;
      line-height: 1.5;
      color: ${(props) => props.theme.text500};
    }
  }

  footer {
    display: flex;
    margin-top: 2rem;
    flex-flow: row wrap;
    gap: 0.5rem;

    ${Button} {
      flex: 1 0 auto;
      transition: opacity 250ms ease-in-out;
    }
  }
`;
const StyledWrapper = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: ${(props) => props.theme.text500};
  white-space: nowrap;
`;

const QuitEventButton = ({ eventPk, group, isOpen, setIsOpen, rsvped }) => {
  const [isQuitting, setIsQuitting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const groupPk = group?.id;

  const handleQuit = useCallback(
    async (e) => {
      e.preventDefault();
      setIsLoading(true);
      let error = "";
      try {
        const response = await api.quitEvent(eventPk, groupPk);
        if (response.error) {
          error = response.error;
        }
      } catch (err) {
        error = err.message;
      }
      if (error) {
        log.error(error);
        return;
      }
      mutate(api.getEventEndpoint("getEvent", { eventPk }));
      setIsLoading(false);
      setIsQuitting(false);
      setIsOpen && setIsOpen(false);
    },
    [eventPk, groupPk, setIsOpen],
  );

  const openDialog = useCallback((e) => {
    if (e) {
      e.preventDefault();
    }
    setIsQuitting(true);
  }, []);

  const closeDialog = useCallback(() => {
    setIsQuitting(false);
    setIsOpen && setIsOpen(false);
  }, [setIsOpen]);

  return (
    <StyledWrapper>
      {!setIsOpen && (
        <a href="" onClick={openDialog}>
          Annuler
        </a>
      )}
      <ResponsiveLayout
        DesktopLayout={Modal}
        MobileLayout={BottomSheet}
        shouldShow={isOpen || isQuitting}
        isOpen={isOpen || isQuitting}
        onClose={closeDialog}
        onDismiss={closeDialog}
        shouldDismissOnClick
        noScroll
      >
        <StyledDialog>
          <main>
            {groupPk ? (
              <>
                <h4>Annuler la participation du groupe à l’événement&nbsp;?</h4>
                <p>
                  <b>{group.name}</b> ne sera plus indiqué comme participant à
                  l’événement.
                  <Spacer size="1rem" />
                  L’événement sera retiré de l’agenda du groupe.
                </p>
              </>
            ) : (
              <>
                <h4>
                  Confirmez-vous que vous ne participez pas à l'événement ?
                </h4>
                <p>
                  Les organisateur·ices de l'événement auront accès à la liste
                  des personnes ayant indiqué leur indisponibilité (nom
                  d'affichage et image de profil).
                </p>
              </>
            )}
          </main>
          <footer>
            <Button color="choose" onClick={closeDialog} disabled={isLoading}>
              Annuler
            </Button>
            <Button
              color="primary"
              onClick={handleQuit}
              isLoading={isLoading}
              disabled={isLoading}
            >
              Je ne participe pas à l'événement
            </Button>
          </footer>
        </StyledDialog>
      </ResponsiveLayout>
    </StyledWrapper>
  );
};
QuitEventButton.propTypes = {
  eventPk: PropTypes.string.isRequired,
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }),
  isOpen: PropTypes.bool,
  rsvped: PropTypes.bool,
  setIsOpen: PropTypes.func,
};
export default QuitEventButton;
