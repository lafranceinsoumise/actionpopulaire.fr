import React, { useCallback, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { BlockSwitchLink } from "./styledComponents";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import Link from "@agir/front/app/Link";
import TextField from "@agir/front/formComponents/TextField";
import Toast from "@agir/front/genericComponents/Toast";

import { signUp } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";

const CountryToggle = styled.button`
  background: transparent;
  border: none;
  font-size: 11px;
  line-height: 1rem;
  cursor: pointer;
  text-align: right;
  width: 100%;
  padding: 0;
  margin-top: -4px;

  &:hover,
  &:focus {
    outline: none;
    text-decoration: underline;
  }
`;
const InputGroup = styled.div`
  display: grid;
  width: 100%;
  margin-top: 1.25rem;
  grid-template-columns: 340px 140px;
  grid-gap: 0.5rem;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: 140px 1fr;
  }

  & > div {
    &:nth-child(1) {
      @media (max-width: ${style.collapse}px) {
        grid-column: span 2;
      }
    }

    &:nth-child(3) {
      @media (min-width: ${style.collapse}px) {
        grid-column: span 2;
      }
    }

    & > label {
      margin-bottom: 0;
    }
  }
`;

const fromGroupEvent = false;

const defaultData = {
  email: "",
  postalCode: "",
  country: "FR",
};

const SignUp = () => {
  const history = useHistory();
  const location = useLocation();

  const [hasCountryField, setHasCountryField] = useState(false);

  const [rgpdChecked, setRgpdChecked] = useState(false);
  const [formData, setFormData] = useState(defaultData);
  const [error, setError] = useState({});

  const showCountryField = useCallback(() => {
    setHasCountryField(true);
  }, []);

  const handleRgpdCheck = useCallback(() => {
    setError({ ...error, rgpd: null });
    setRgpdChecked(!rgpdChecked);
  }, [error, rgpdChecked]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setError((state) => state && { ...state, [name]: null });
    setFormData((state) => ({ ...state, [name]: value }));
  }, []);

  const handleChangeCountry = useCallback((country) => {
    setError((state) => state && { ...state, country: null });
    setFormData((state) => ({ ...state, country }));
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
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
      const route = routeConfig.codeSignup.getLink();
      history.push(route, { ...location.state, email: formData.email });
    },
    [formData, history, location, rgpdChecked]
  );

  return (
    <form
      style={{ width: "500px", maxWidth: "100%", paddingBottom: "1.5rem" }}
      onSubmit={handleSubmit}
    >
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
            error={error && error.postalCode}
            placeholder=""
            onChange={handleChange}
            value={formData.postalCode}
          />
          {hasCountryField === false ? (
            <CountryToggle type="button" onClick={showCountryField}>
              J'habite à l'étranger
            </CountryToggle>
          ) : null}
        </div>
        {hasCountryField && (
          <div>
            <CountryField
              label="Pays"
              name="country"
              error={error && error.country}
              placeholder=""
              onChange={handleChangeCountry}
              value={formData.country}
            />
            {hasCountryField === false ? (
              <CountryToggle type="button" onClick={showCountryField}>
                J'habite à l'étranger
              </CountryToggle>
            ) : null}
          </div>
        )}
      </InputGroup>

      <div style={{ paddingTop: "1rem" }}>
        <CheckboxField
          name="rgpd"
          label={
            <>
              J'accepte que mes informations soient traitées par Action
              Populaire, conformément à la&nbsp;
              <a
                href="https://infos.actionpopulaire.fr/mentions-legales/"
                target="_blank"
                rel="noopener noreferrer"
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
      {error && !!error.global && <Toast>{error.global}</Toast>}

      <Button
        type="submit"
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
    </form>
  );
};

export default SignUp;
