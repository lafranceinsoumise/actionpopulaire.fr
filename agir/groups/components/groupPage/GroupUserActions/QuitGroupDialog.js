import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";

const StyledDialog = styled.div`
  max-width: 415px;
  margin: 40px auto;
  background-color: ${style.white};
  border-radius: 8px;
  padding: 1rem;

  @media (max-width: ${style.collapse}px) {
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
      justify-content: center;
      transition: opacity 250ms ease-in-out;
    }

    ${Button} + ${Button} {
      margin: 0.5rem 0 0;
    }
  }
`;

const QuitGroupButton = (props) => {
  const {
    groupName,
    isActiveMember,
    shouldShow,
    isLoading,
    onDismiss,
    onConfirm,
  } = props;

  return (
    <ResponsiveLayout
      DesktopLayout={Modal}
      MobileLayout={BottomSheet}
      shouldShow={shouldShow}
      isOpen={shouldShow}
      onClose={onDismiss}
      onDismiss={onDismiss}
      shouldDismissOnClick
      noScroll
    >
      <StyledDialog>
        <main>
          {isActiveMember ? (
            <h4>Quitter le groupe {groupName}&nbsp;?</h4>
          ) : (
            <h4>Ne plus suivre le groupe {groupName}&nbsp;?</h4>
          )}
          {isActiveMember ? (
            <p>
              Vous ne serez plus considéré·e comme membre actif de votre groupe.
              <br />
              Vous ne recevez plus les messages postés sur Action Populaire
              destinés aux membres actifs.
            </p>
          ) : (
            <p>
              Vous ne recevrez plus les actualités de ce groupe.
              <br />
              Vous pouvez suivre ce groupe à nouveau à tout moment.
            </p>
          )}
        </main>
        <footer>
          <Button color="danger" onClick={onConfirm} disabled={isLoading}>
            {isActiveMember ? "Quitter le groupe" : "Ne plus suivre"}
          </Button>
          <Button color="default" onClick={onDismiss} disabled={isLoading}>
            Annuler
          </Button>
        </footer>
      </StyledDialog>
    </ResponsiveLayout>
  );
};
QuitGroupButton.propTypes = {
  groupName: PropTypes.string.isRequired,
  isActiveMember: PropTypes.bool,
  shouldShow: PropTypes.bool,
  isLoading: PropTypes.bool,
  onConfirm: PropTypes.func.isRequired,
  onDismiss: PropTypes.func.isRequired,
};
export default QuitGroupButton;
