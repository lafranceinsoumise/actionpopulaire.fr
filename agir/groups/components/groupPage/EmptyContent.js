import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

import emptyMessagesBackground from "./images/empty-messages-bg.svg";

const EmptyContentIllustration = styled.div`
  margin: 0 auto 22px;
  width: 168px;
  height: 161px;
  background-image: url(${emptyMessagesBackground});
  background-position: center center;
  background-repeat: no-repeat;
  background-size: cover;
`;
const StyledIcon = styled.div`
  position: relative;
  height: 40px;
  width: 40px;

  ${RawFeatherIcon} {
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;

    &:first-child {
      transform: translate(7px, 7px);
    }
  }
`;
const StyledContent = styled.div``;
const StyledEmptyContent = styled.div`
  display: flex;
  flex-flow: row nowrap;
  padding: 30px;
  align-items: center;
  border: 1px solid ${style.black100};
  margin-bottom: 1.5rem;
  background-color: white;

  @media (max-width: ${style.collapse}px) {
    flex-direction: column;
  }

  ${StyledIcon} {
    margin-right: 20px;

    @media (max-width: ${style.collapse}px) {
      margin-right: 0;
      margin-bottom: 22px;
    }
  }

  ${StyledContent} {
    @media (max-width: ${style.collapse}px) {
      text-align: center;
    }

    p {
      max-width: 546px;
      margin: 0 auto;

      @media (max-width: ${style.collapse}px) {
        max-width: 264px;
      }
    }

    p + p {
      @media (max-width: ${style.collapse}px) {
        margin: 0.5rem auto;
      }
    }

    a,
    strong {
      font-weight: 600;
      font-size: inherit;
      line-height: inherit;
    }

    h6 {
      color: ${style.redNSP};
      text-transform: uppercase;
      font-size: 0.875rem;
      font-weight: 500;
    }

    h3 {
      font-size: 1.625rem;
      line-height: 1.5;
      font-weight: 700;
      margin-bottom: 22px;
      max-width: 588px;

      @media (max-width: ${style.collapse}px) {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
      }
    }

    ul {
      list-style: none;
      font-size: 0.875rem;
      line-height: 1.5;
      padding: 0;
      max-width: 588px;

      li {
        display: flex;
        align-items: flex-start;
        text-align: left;
        margin-bottom: 0.5rem;

        ${RawFeatherIcon} {
          margin-right: 11px;
          margin-top: 3px;
          width: 1rem;
          height: 1rem;
        }
      }
    }

    ${Button} {
      margin-top: 1.5rem;
    }
  }
`;

const EmptyContent = (props) => {
  const { icon, children } = props;
  return (
    <StyledEmptyContent style={props.style}>
      {icon ? (
        <StyledIcon>
          <RawFeatherIcon
            name={icon}
            width="40px"
            height="40px"
            strokeWidth="0"
            svgStyle={{ fill: style.black50 }}
          />
          <RawFeatherIcon
            name={icon}
            width="40px"
            height="40px"
            strokeWidth="2"
          />
        </StyledIcon>
      ) : null}
      <StyledContent>{children}</StyledContent>
    </StyledEmptyContent>
  );
};
EmptyContent.propTypes = {
  icon: PropTypes.string,
  style: PropTypes.object,
  children: PropTypes.node,
};

export const MemberEmptyEvents = () => (
  <EmptyContent icon="calendar">
    <p>Ce groupe n’a pas encore créé d’événement.</p>
  </EmptyContent>
);

export const ManagerEmptyEvents = () => (
  <EmptyContent icon="calendar">
    <p>Vous n’avez pas encore créé d’événement.</p>
    <p>
      Besoin d’idée ? Consultez notre{" "}
      <a href="https://infos.actionpopulaire.fr/groupes/nouvelle-equipe/">
        guide pour les nouveaux groupes
      </a>
    </p>
  </EmptyContent>
);

export const EmptyReports = () => (
  <EmptyContent icon="file-text">
    <p>Votre groupe n’a pas encore publié de compte-rendu.</p>
    <p>
      Ajoutez-en à vos événement passés pour tenir au courant les membres de
      comment s’est déroulé votre événement&nbsp;!
    </p>
  </EmptyContent>
);

export const EmptyMessages = ({ onClickSendMessage }) => (
  <EmptyContent
    style={{
      marginTop: "1.5rem",
      flexDirection: "column",
      textAlign: "center",
      padding: "40px",
    }}
  >
    <EmptyContentIllustration aria-hidden="true" />
    <h6>Nouveau</h6>
    <h3>Lancez une première conversation dans votre groupe&nbsp;!</h3>
    <ul>
      <li>
        <RawFeatherIcon name="heart" />
        <span>
          Fini les boucles d’e-mails&nbsp;! Discustez de vos prochaines actions
          sur Action Populaire.
        </span>
      </li>
      <li>
        <RawFeatherIcon name="edit-3" />
        <span>
          Les animateurs·rices et gestionnaires sont{" "}
          <strong>à l'initiative de la discussion</strong>
        </span>
      </li>
      <li>
        <RawFeatherIcon name="lock" />
        <span>
          Les messages ne sont <strong>visibles</strong> que par les membres du
          groupe.
        </span>
      </li>
      <li>
        <RawFeatherIcon name="mail" />
        <span>
          Tous vos membres <strong>recevront un e-mail</strong> avec le contenu
          de votre message et pourront y <strong>répondre sur le site</strong>.
        </span>
      </li>
    </ul>
    {onClickSendMessage ? (
      <Button color="secondary" onClick={onClickSendMessage}>
        Publier un message
      </Button>
    ) : null}
  </EmptyContent>
);
EmptyMessages.propTypes = {
  onClickSendMessage: PropTypes.func,
};
export default EmptyContent;
