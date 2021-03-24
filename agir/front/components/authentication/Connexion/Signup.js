import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Toast from "@agir/front/genericComponents/Toast";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import Link from "@agir/front/app/Link";
import { signUp } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory, useLocation } from "react-router-dom";
import { BlockSwitchLink } from "./styledComponents";

const InputGroup = styled.div`
  display: inline-flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 1.25rem;
  > div:nth-child(1) {
    width: 340px;
  }
  > div:nth-child(2) {
    width: 140px;
  }

  @media (max-width: ${style.collapse}px) {
    display:block;
    > div:nth-child(1) {
      width: 100%;
    }
`;

const fromGroupEvent = false;

const defaultData = {
  email: "",
  postalCode: "",
};

const SignUp = () => {
  const history = useHistory();
  const location = useLocation();
  const [rgpdChecked, setRgpdChecked] = useState(false);
  const [formData, setFormData] = useState(defaultData);
  const [error, setError] = useState({});

  const handleRgpdCheck = () => {
    setRgpdChecked(!rgpdChecked);
    setError({ ...error, rgpd: null });
  };

  const handleChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = e.target.value;
    setFormData(newFormData);
  };

  const handleSubmit = async () => {
    setError({});
    if (!rgpdChecked) {
      setError({
        rgpd:
          "Vous devez accepter la politique de conservation des données pour continuer",
      });
      return;
    }
    const data = await signUp(formData);
    if (data.error) {
      setError(data.error);
      return;
    }
    location.state.email = formData.email;
    const route = routeConfig.codeSignup.getLink();
    history.push(route);
  };

  return (
    <div style={{ width: "500px", maxWidth: "100%", paddingBottom: "1.5rem" }}>
      {!fromGroupEvent ? (
        <h1>Je m'inscris</h1>
      ) : (
        <h1 style={{ fontSize: "26px" }}>
          Je m’inscris pour participer à l’événement
        </h1>
      )}

      <BlockSwitchLink>
        <span>Déjà inscrit·e ?</span>
        &nbsp;
        <span>
          <Link route="login">Je me connecte</Link>
        </span>
      </BlockSwitchLink>

      <InputGroup>
        <div>
          <TextField
            label="Email"
            name="email"
            error={error && error.email}
            placeholder=""
            onChange={handleChange}
            value={formData.email}
          />
        </div>
        <div>
          <TextField
            label="Code postal"
            name="postalCode"
            error={error && error.location_zip}
            placeholder=""
            onChange={handleChange}
            value={formData.postalCode}
          />
        </div>
      </InputGroup>

      <div style={{ marginTop: "1rem" }}>
        <CheckboxField
          name="rgpd"
          label={
            <>
              J'accepte que mes informations soient traitées par Action
              Populaire, conformément à la&nbsp;
              <a
                href="https://infos.actionpopulaire.fr/mentions-legales/"
                target="_blank"
              >
                politique de conservation des données
              </a>
            </>
          }
          value={rgpdChecked}
          onChange={handleRgpdCheck}
        />
      </div>

      {error && !!error.rgpd && <Toast>{error.rgpd}</Toast>}

      <Button
        onClick={handleSubmit}
        color="primary"
        style={{
          marginTop: "2rem",
          maxWidth: "100%",
          width: "100%",
          justifyContent: "center",
        }}
      >
        {!fromGroupEvent ? "Créer mon compte" : "Je participe !"}
      </Button>
    </div>
  );
};

export default SignUp;
