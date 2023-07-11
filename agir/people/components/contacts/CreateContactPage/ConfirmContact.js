import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledWrapper = styled.div`
  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    margin-bottom: 1.5rem;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.25rem;
    }
  }

  h4,
  p,
  ul {
    padding: 0;
    margin: 0;
  }

  ul {
    padding-left: 1rem;

    li + li {
      margin-top: 0.25rem;
    }
  }

  footer {
    line-height: 0;
    @media (max-width: ${style.collapse}px) {
      display: flex;
      flex-flow: column-reverse nowrap;

      ${Button} {
        width: 100%;
      }
    }
  }
`;

const ConfirmContact = (props) => {
  const { data, onBack, onConfirm, isLoading } = props;
  const newsletters = [
    data.newsletters.includes("2022_exceptionnel") &&
      "les informations très importantes",
    data.newsletters.includes("2022") && "hebdomadaires",
    data.group?.id &&
      data.hasGroupNotifications &&
      "les actualités du groupe d'action",
  ].filter(Boolean);
  return (
    <StyledWrapper>
      <h2>Confirmer les informations</h2>
      <div>
        <h4>
          {data.firstName} {data.lastName}
        </h4>
        <p>{data.phone}</p>
        {data.address ? <p>{data.address}</p> : null}
        <p>{`${data.zip} ${data.city || ""} ${data.country || ""}`.trim()}</p>
        <p style={{ color: style.primary500 }}>{data.email}</p>
      </div>
      <Spacer size="1.5rem" />
      <ul>
        {data.is2022 ? <li>Soutien Jean-Luc Mélenchon pour 2022</li> : null}
        {newsletters.length > 0 ? (
          <li>{`Recevra ${newsletters.join(", ")}`}</li>
        ) : null}
        {data.newsletters.includes("2022_liaison") ? (
          <li>Sera correspondant·e de l’immeuble ou de village</li>
        ) : null}
        {data.group?.id ? (
          <li>
            Ces informations seront accessibles aux gestionnaires et
            animateur·ices du groupe <strong>{data.group.name}</strong>
          </li>
        ) : null}
      </ul>
      <Spacer size="2rem" />
      <p>Le contact recevra un e-mail lui confirmant ces informations.</p>
      <Spacer size="0.5rem" />
      <p>
        En enregistrant cette personne vous confirmez avoir reçu son
        consentement oral. Tout abus sera sanctionné.
      </p>
      <Spacer size="1rem" />
      <footer>
        <Button icon="arrow-left" onClick={onBack} disabled={isLoading}>
          Modifier
        </Button>
        <Spacer style={{ display: "inline-block" }} size="1rem" />
        <Button color="secondary" onClick={onConfirm} disabled={isLoading}>
          Enregistrer le contact
        </Button>
      </footer>
    </StyledWrapper>
  );
};

ConfirmContact.propTypes = {
  data: PropTypes.shape({
    firstName: PropTypes.string.isRequired,
    lastName: PropTypes.string.isRequired,
    zip: PropTypes.string.isRequired,
    phone: PropTypes.string,
    email: PropTypes.string.isRequired,
    is2022: PropTypes.bool.isRequired,
    newsletters: PropTypes.arrayOf(PropTypes.string).isRequired,
    group: PropTypes.object,
    hasGroupNotifications: PropTypes.bool,
    address: PropTypes.string,
    city: PropTypes.string,
  }),
  onBack: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
};
export default ConfirmContact;
