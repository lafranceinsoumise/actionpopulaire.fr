import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import Spacer from "@agir/front/genericComponents/Spacer";
import StyledDialog from "./StyledDialog";

const JoinGroupDialog = (props) => {
  const { shouldShow, isLoading, isActiveMember, groupName, onQuit, onClose } =
    props;

  return (
    <ModalConfirmation
      shouldShow={shouldShow}
      onClose={!isLoading ? onClose : undefined}
      shouldDismissOnClick={false}
    >
      <StyledDialog>
        <header>
          {isActiveMember ? (
            <h3>Quitter le groupe {groupName}&nbsp;?</h3>
          ) : (
            <h3>Ne plus suivre le groupe {groupName}&nbsp;?</h3>
          )}
        </header>
        <article>
          {isActiveMember ? (
            <p>
              Voulez-vous vraiment quitter le groupe&nbsp;? Vous ne recevrez
              plus aucune actualité de ce groupe.
              <Spacer size=".5rem" />
              Vous pourrez rejoindre le groupe à nouveau à tout moment.
            </p>
          ) : (
            <p>
              Vous ne recevrez plus les actualités de ce groupe.
              <Spacer size=".5rem" />
              Vous pouvez suivre ce groupe à nouveau à tout moment.
            </p>
          )}
        </article>
        <footer>
          <Button
            color="danger"
            onClick={onQuit}
            disabled={isLoading}
            loading={isLoading}
          >
            {isActiveMember ? "Quitter le groupe" : "Ne plus suivre"}
          </Button>
          <Button onClick={onClose} disabled={isLoading}>
            Annuler
          </Button>
        </footer>
      </StyledDialog>
    </ModalConfirmation>
  );
};

JoinGroupDialog.propTypes = {
  shouldShow: PropTypes.bool,
  isLoading: PropTypes.bool,
  isActiveMember: PropTypes.bool,
  groupName: PropTypes.string.isRequired,
  onQuit: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default JoinGroupDialog;
