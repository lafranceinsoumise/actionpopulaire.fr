import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";

import * as api from "@agir/events/common/api";
import { mutate } from "swr";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

const StyledDialog = styled.div`
  max-width: 415px;
  margin: 40px auto;
  background-color: ${(props) => props.theme.white};
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
    }
  }
  footer {
    display: flex;
    margin-top: 1.5rem;
    flex-flow: column nowrap;

    ${Button} {
      flex: 1 1 auto;
      transition: opacity 250ms ease-in-out;
    }

    ${Button} + ${Button} {
      margin: 0.5rem 0 0;
    }
  }
`;
const StyledWrapper = styled.div`
  font-size: 1rem;
  font-weight: 600;
  font-color: ${(props) => props.theme.black500};
`;

const QuitEventButton = ({ id }) => {
  const [isQuitting, setIsQuitting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleQuit = useCallback(
    async (e) => {
      e.preventDefault();
      setIsLoading(true);
      let error = "";
      try {
        const response = await api.quitEvent(id);
        if (response.error) {
          error = response.error;
        }
      } catch (err) {
        error = err.message;
      }
      setIsLoading(false);
      setIsQuitting(false);
      if (error) {
        log.error(error);
        return;
      }
      mutate(api.getEventEndpoint("getEvent", { eventPk: id }), (event) => ({
        ...event,
        rsvped: false,
      }));
    },
    [id]
  );

  const openDialog = useCallback((e) => {
    if (e) {
      e.preventDefault();
    }
    setIsQuitting(true);
  }, []);

  const closeDialog = useCallback(() => {
    setIsQuitting(false);
  }, []);

  return (
    <StyledWrapper>
      <a href="" onClick={openDialog}>
        Annuler
      </a>
      <ResponsiveLayout
        DesktopLayout={Modal}
        MobileLayout={BottomSheet}
        shouldShow={isQuitting}
        isOpen={isQuitting}
        onClose={closeDialog}
        onDismiss={closeDialog}
        shouldDismissOnClick
        noScroll
      >
        <StyledDialog>
          <main>
            <h4>Annuler ma participation à l'événement</h4>
            <p>
              Souhaitez-vous réellement ne plus participer à l'événement&nbsp;?
            </p>
          </main>
          <footer>
            <Button color="danger" onClick={handleQuit} disabled={isLoading}>
              Quitter l'événement
            </Button>
            <Button color="default" onClick={closeDialog} disabled={isLoading}>
              Annuler
            </Button>
          </footer>
        </StyledDialog>
      </ResponsiveLayout>
    </StyledWrapper>
  );
};
QuitEventButton.propTypes = {
  id: PropTypes.string.isRequired,
};
export default QuitEventButton;
