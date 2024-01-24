import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
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

    li {
      list-style-type: "— ";
    }

    li + li {
      margin-top: 0.25rem;
    }
  }

  footer {
    display: flex;
    line-height: 0;

    @media (max-width: ${style.collapse}px) {
      flex-flow: column-reverse nowrap;

      ${Button} {
        width: 100%;
      }
    }
  }
`;

const ConfirmContact = (props) => {
  const { data, onBack, onConfirm, isLoading } = props;

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
        {data.isLiaison && (
          <li>
            Cette personne sera correspondant·e de son immeuble ou de son
            village pour les campagnes de la France insoumise
          </li>
        )}
        {data.group?.id && (
          <li>
            Les coordonnées de cette personnes seront accessibles aux
            gestionnaires et animateur·ices du groupe{" "}
            <strong>{data.group.name}</strong>
          </li>
        )}
        {data.subscribed || data.group?.id ? (
          <li>
            Cette personne recevra{" "}
            {[
              data.subscribed && "les informations de la France insoumise",
              data.group?.name &&
                `l'actualité du groupe d'action ${data.group.name}`,
            ]
              .filter(Boolean)
              .join(" et ")}
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
    subscribed: PropTypes.bool.isRequired,
    isLiaison: PropTypes.bool.isRequired,
    group: PropTypes.object,
    hasGroupNotifications: PropTypes.bool,
    address: PropTypes.string,
    city: PropTypes.string,
    country: PropTypes.string,
  }),
  onBack: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
};
export default ConfirmContact;
