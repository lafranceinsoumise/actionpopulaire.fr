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
  const { data, onBack, onConfirm } = props;
  return (
    <StyledWrapper>
      <h2>Confirmer les informations</h2>
      <div>
        <h4>
          {data.firstName} {data.lastName}
        </h4>
        <p>{data.phone}</p>
        {data.liaisonAddress ? <p>{data.liaisonAddress}</p> : null}
        <p>
          {data.zip} {data.liaisonCity}
        </p>
        <p style={{ color: style.primary500 }}>{data.email}</p>
      </div>
      <Spacer size="1.5rem" />
      <ul>
        <li>Soutien Jean-Luc Mélenchon pour 2022</li>
        {data.nl2022 || data.nl2022_exceptionnel || data.isGroupFollower ? (
          <li>{`Recevra ${[
            data.nl2022_exceptionnel && "les informations très importantes",
            data.nl2022 && "hebdomadaires",
            data.isGroupFollower && "les actualités du groupe d'action",
          ]
            .filter(Boolean)
            .join(", ")}`}</li>
        ) : null}
        {data.isLiaison ? <li>Sera correspondant·e de l’immeuble</li> : null}
      </ul>
      <Spacer size="2.5rem" />
      <footer>
        <Button icon="arrow-left" onClick={onBack}>
          Modifier
        </Button>
        <Spacer style={{ display: "inline-block" }} size="1rem" />
        <Button color="secondary" onClick={onConfirm}>
          Enregistrer le soutien
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
    nl2022_exceptionnel: PropTypes.bool,
    nl2022: PropTypes.bool,
    isGroupFollower: PropTypes.bool,
    isLiaison: PropTypes.bool,
    liaisonAddress: PropTypes.string,
    liaisonCity: PropTypes.string,
  }),
  onBack: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
};
export default ConfirmContact;
