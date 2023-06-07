import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import JLM_rounded from "@agir/front/genericComponents/images/JLM_rounded.png";

import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { updateProfile } from "@agir/front/authentication/api";

const Container = styled.form`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 7rem 2rem 1.5rem;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;

  @media (max-width: ${style.collapse}px) {
    max-width: 400px;
    padding: 3rem 2rem 1.5rem;
  }

  h2,
  p {
    margin: 0;
    max-width: 100%;
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    line-height: 1.5;
    text-align: center;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.125rem;
    }

    span {
      display: block;
    }
  }

  & > ${Button} {
    max-width: 100%;

    @media (max-width: ${style.collapse}px) {
      width: 100%;
    }

    &[type="button"] {
      background-color: transparent;
      color: ${style.black500};
      font-size: 0.875rem;
      font-weight: 400;
    }
  }
`;

const ChooseCampaign = ({ fromSignup, dismiss }) => {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setSubmitted(true);
      await updateProfile({ isPoliticalSupport: true });
      await dismiss();
      setSubmitted(false);
    },
    [dismiss]
  );

  return (
    <div>
      <Hide under>
        <div style={{ position: "fixed" }}>
          <Link route="events">
            <LogoAP
              style={{ marginTop: "2rem", paddingLeft: "2rem", width: "200px" }}
            />
          </Link>
        </div>
      </Hide>
      <Container onSubmit={handleSubmit}>
        {fromSignup && (
          <div
            style={{
              display: "inline-flex",
              fontWeight: 600,
              padding: "0.5rem 1rem",
              backgroundColor: style.green100,
              marginBottom: "2rem",
              flex: "0 0 auto",
              alignSelf: "center",
            }}
          >
            <FeatherIcon
              name="check"
              color="green"
              strokeWidth={4}
              width="1rem"
              style={{ marginRight: "12px" }}
            />
            Votre compte a été créé
          </div>
        )}
        <img
          src={JLM_rounded}
          width="114"
          height="114"
          alt="Jean-Luc Mélenchon"
        />
        <Spacer size="2rem" />
        <h2>
          <span>Vous ne soutenez pas encore</span>{" "}
          <span>l'Union Populaire&nbsp;!</span>
        </h2>
        <Spacer size="2rem" />
        <Button color="primary" type="submit" disabled={submitted}>
          Confirmer mon soutien et continuer
        </Button>
        <Spacer size="1rem" />
        <Button type="button" onClick={dismiss}>
          Passer cette étape
        </Button>
      </Container>
    </div>
  );
};
ChooseCampaign.propTypes = {
  fromSignup: PropTypes.bool,
  dismiss: PropTypes.func.isRequired,
};
export default ChooseCampaign;
