import PropTypes from "prop-types";
import React, { Fragment, useMemo } from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";
import Button from "@agir/front/genericComponents/Button.js";
import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { StyledTitle } from "@agir/groups/groupPage/GroupSettings/styledComponents.js";

const [REFERENT, MANAGER /*, MEMBER */] = [100, 50, 10];

const MainPanel = (props) => {
  const { editManager, editReferent, members, is2022, routes } = props;
  const referents = useMemo(
    () => members.filter((member) => member.membershipType === REFERENT),
    [members]
  );
  const managers = useMemo(
    () => members.filter((member) => member.membershipType === MANAGER),
    [members]
  );
  return (
    <>
      <StyledTitle>Animateurs et animatrices</StyledTitle>
      <span style={{ color: style.black700 }}>
        Les animateur·ices organisent la vie{" "}
        {is2022 ? "de l'équipe" : "du groupe"}.
      </span>
      <Spacer size=".5rem" />
      <span style={{ color: style.black700 }}>
        Pour respecter la{" "}
        <a
          href={
            is2022
              ? "https://infos.actionpopulaire.fr/charte-des-equipes-de-soutien-nous-sommes-pour/"
              : "https://lafranceinsoumise.fr/groupes-appui/charte-groupes-dappui-de-france-insoumise/"
          }
        >
          charte des {is2022 ? "équipes de soutien" : "groupes d'action"}
        </a>
        , votre {is2022 ? "équipe" : "groupe"} doit être animée à parité de
        genre.
      </span>
      <Spacer size="1.5rem" />
      <GroupMemberList
        members={referents}
        addButtonLabel="Ajouter votre binôme"
        onAdd={
          referents.length < 2 && members.length > 1 ? editReferent : undefined
        }
      />
      <Spacer size="1.5rem" />
      {routes?.animationChangeRequest && (
        <a
          href={routes.animationChangeRequest}
          style={{ display: "flex", alignItems: "center" }}
        >
          <FeatherIcon name="arrow-right" width="1rem" height="1rem" />
          &ensp;Changer l’animation {is2022 ? "de l'équipe" : "du groupe"}
        </a>
      )}
      {routes?.animationChangeRequest && routes?.referentResignmentRequest && (
        <Spacer size="0.5rem" />
      )}
      {routes?.referentResignmentRequest && (
        <a
          href={routes.referentResignmentRequest}
          style={{ display: "flex", alignItems: "center" }}
        >
          <FeatherIcon name="arrow-right" width="1rem" height="1rem" />
          &ensp;Je ne souhaite plus être animateur ou animatrice
        </a>
      )}
      {(routes?.animationChangeRequest ||
        routes?.referentResignmentRequest) && <Spacer size="1.5rem" />}
      <StyledTitle>Gestionnaires</StyledTitle>
      <span style={{ color: style.black700 }}>
        Ajoutez des gestionnaires pour vous assister sur Action Populaire.
      </span>
      <Spacer size="0.5rem" />
      <span style={{ color: style.black700 }}>
        Ces derniers ont accès à la liste des membres, peuvent modifier les
        informations et créer des événements au nom{" "}
        {is2022 ? "de l'équipe" : "du groupe"}.
      </span>
      <Spacer size="1.5rem" />
      <GroupMemberList
        members={managers}
        addButtonLabel="Ajouter un·e gestionnaire"
        onAdd={editManager}
      />
      {routes?.certificationRequest && (
        <>
          <Spacer size="1.5rem" />
          <StyledTitle>Certifier le groupe</StyledTitle>
          <span style={{ color: style.black700 }}>
            Votre groupe n'est pas encore certifié. Vous pouvez en demander la
            certification en cliquant sur le bouton
          </span>
          <Spacer size="1.5rem" />
          <Button as="a" href={routes.certificationRequest} color="primary">
            Demander la certification
          </Button>
        </>
      )}
      {!is2022 && routes?.deleteGroup && (
        <>
          <hr />
          <a href={routes.deleteGroup} style={{ color: style.redNSP }}>
            Supprimer {is2022 ? "l'équipe" : "le groupe"}
          </a>
        </>
      )}
    </>
  );
};

MainPanel.propTypes = {
  members: PropTypes.arrayOf(PropTypes.object),
  editManager: PropTypes.func,
  editReferent: PropTypes.func,
  is2022: PropTypes.bool,
  routes: PropTypes.shape({
    certificationRequest: PropTypes.string,
    animationChangeRequest: PropTypes.string,
    referentResignmentRequest: PropTypes.string,
    deleteGroup: PropTypes.string,
  }),
};

export default MainPanel;
