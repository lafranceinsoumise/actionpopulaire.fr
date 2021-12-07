import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import Spacer from "@agir/front/genericComponents/Spacer";
import StyledDialog from "./StyledDialog";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

export const JoinGroup = (props) => {
  const {
    id,
    step,
    isLoading,
    groupName,
    groupReferents,
    personName,
    personalInfoConsent,
    onJoin,
    onUpdate,
    onClose,
  } = props;

  const user = useSelector(getUser);
  const [messageModalOpen, setMessageModalOpen] = useState(false);

  const sendPrivateMessage = async (msg) => {
    const message = {
      subject: msg.subject,
      text: msg.text,
    };
    const result = await groupAPI.createPrivateMessage(id, message);
    onSelectMessage(result.data.id);
    onClose();
  };

  switch (step) {
    case 1:
      return (
        <StyledDialog>
          <header>
            <h3>Rejoindre {groupName}</h3>
          </header>
          <article>
            Les animateur·ices seront informé·es de votre arrivée et vous
            pourrez rencontrer les membres du groupe&nbsp;!
          </article>
          <footer>
            <Button
              disabled={isLoading}
              loading={isLoading}
              onClick={onJoin}
              color="primary"
              block
              wrap
            >
              Je rejoins&nbsp;!
            </Button>
            <Button disabled={isLoading} onClick={onClose} block wrap>
              Annuler
            </Button>
          </footer>
        </StyledDialog>
      );
    case 2: {
      let referentNames = groupReferents
        .map((referent, i) => {
          if (i === 0) {
            return referent.displayName;
          }
          if (i === groupReferents.length - 1) {
            return " et " + referent.displayName;
          }
          return ", " + referent.displayName;
        })
        .join("");

      const givePersonalInfoConsent = () =>
        onUpdate({ personalInfoConsent: true });

      const denyPersonalInfoConsent = () =>
        onUpdate({ personalInfoConsent: false });

      return (
        <StyledDialog>
          <header>
            <h3>Bienvenue dans le groupe, {personName}&nbsp;!&nbsp;👍</h3>
          </header>
          <article>
            <strong>
              Faites la rencontre avec {referentNames} qui animent ce groupe.
            </strong>
            <Spacer size=".5rem" />
            Partagez vos coordonnées (nom complet, téléphone et adresse) avec
            eux pour qu'ils puissent prendre contact avec vous.
            <Spacer size=".5rem" />
            Vous pourrez retirer cette autorisation à tout moment. C'est
            maintenant que tout se joue&nbsp;!
          </article>
          <footer>
            <Button
              disabled={isLoading}
              loading={isLoading}
              onClick={givePersonalInfoConsent}
              block
              wrap
            >
              Partager mes coordonnées avec {referentNames}
            </Button>
            <Button
              disabled={isLoading}
              onClick={denyPersonalInfoConsent}
              block
              wrap
            >
              Passer cette étape
            </Button>
          </footer>
        </StyledDialog>
      );
    }
    case 3: {
      return (
        <>
          <StyledDialog>
            <header>
              <h3>Présentez-vous&nbsp;!</h3>
            </header>
            <article>
              <strong>
                {personalInfoConsent
                  ? "C’est noté, les gestionnaires du groupe pourront vous contacter sur la messagerie d’Action Populaire, par e-mail et par téléphone."
                  : "C’est noté, les gestionnaires du groupe pourront vous contacter sur la messagerie d’Action Populaire et par e-mail."}
              </strong>
              <Spacer size=".5rem" />
              Envoyez-leur un message pour vous présenter&nbsp;:
              <Spacer size="1rem" />
              <footer>
                <Button
                  color="primary"
                  block
                  wrap
                  onClick={() => setMessageModalOpen(true)}
                >
                  Je me présente&nbsp;! &nbsp;
                  <RawFeatherIcon name="mail" width="1.5rem" height="1.5rem" />
                </Button>
                <Button disabled={isLoading} onClick={onClose} block wrap>
                  Plus tard
                </Button>
              </footer>
            </article>
          </StyledDialog>
          <MessageModal
            shouldShow={messageModalOpen}
            user={user}
            privateGroupId={id}
            onSend={sendPrivateMessage}
            onClose={() => setMessageModalOpen(false)}
          />
        </>
      );
    }
    default:
      return null;
  }
};

JoinGroup.propTypes = {
  step: PropTypes.number.isRequired,
  isLoading: PropTypes.bool,
  personName: PropTypes.string.isRequired,
  groupName: PropTypes.string.isRequired,
  groupReferents: PropTypes.arrayOf(
    PropTypes.shape({
      displayName: PropTypes.string.isRequired,
    })
  ).isRequired,
  personalInfoConsent: PropTypes.bool,
  onJoin: PropTypes.func.isRequired,
  onUpdate: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

const JoinGroupDialog = (props) => {
  const { step, isLoading, onClose } = props;

  return (
    <ModalConfirmation
      shouldShow={step > 0}
      onClose={!isLoading ? onClose : undefined}
      shouldDismissOnClick={false}
    >
      <JoinGroup {...props} />
    </ModalConfirmation>
  );
};

JoinGroupDialog.propTypes = {
  step: PropTypes.number.isRequired,
  isLoading: PropTypes.bool,
  onClose: PropTypes.func.isRequired,
};

export default JoinGroupDialog;
