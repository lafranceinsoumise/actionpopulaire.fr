import React, { useCallback, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { BlockSwitchLink } from "./styledComponents";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import Link from "@agir/front/app/Link";
import TextField from "@agir/front/formComponents/TextField";
import StaticToast from "@agir/front/genericComponents/StaticToast";

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

  @media (max-width: ${style.collapse}px) {
    text-align: left;
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
  const [moralAgreementChecked, setMoralAgreementChecked] = useState(false);
  const [formData, setFormData] = useState(defaultData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState({});

  const showCountryField = useCallback(() => {
    setHasCountryField(true);
  }, []);

  const handleRgpdCheck = useCallback(
    (e) => {
      setError({ ...error, agreements: null });
      setRgpdChecked(e.target.checked);
    },
    [error],
  );

  const handleMoralAgreementCheck = useCallback(
    (e) => {
      setError({ ...error, agreements: null });
      setMoralAgreementChecked(e.target.checked);
    },
    [error],
  );

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
      if (!rgpdChecked || !moralAgreementChecked) {
        setError({
          agreements:
            "Vous devez accepter la politique de conservation des données et l'engagement ci-dessus pour pouvoir continuer",
        });
        return;
      }
      setIsLoading(true);
      const data = await signUp(formData, location?.state?.next);
      setIsLoading(false);
      if (data.error) {
        setError(data.error);
        return;
      }
      const route = routeConfig.codeSignup.getLink();
      history.push(route, { ...(location.state || {}), email: formData.email });
    },
    [formData, history, location, rgpdChecked, moralAgreementChecked],
  );

  return (
    <form
      style={{ width: "500px", maxWidth: "100%", paddingBottom: "1.5rem" }}
      onSubmit={handleSubmit}
      disabled={isLoading}
    >
      {location.state?.from === "event" ? (
        <h1 style={{ fontSize: "26px" }}>
          Je m’inscris pour participer à l’événement
        </h1>
      ) : location.state?.from === "group" ? (
        <h1 style={{ fontSize: "26px" }}>
          Je m’inscris pour rejoindre le groupe
        </h1>
      ) : (
        <h1>Je m'inscris</h1>
      )}

      <BlockSwitchLink>
        <span>Déjà inscrit·e ?</span>
        &nbsp;
        <span>
          <Link route="login" state={location.state}>
            Je me connecte
          </Link>
        </span>
      </BlockSwitchLink>

      <InputGroup>
        <div>
          <TextField
            label="Email"
            name="email"
            error={error && error.email}
            onChange={handleChange}
            value={formData.email}
            type="email"
            disabled={isLoading}
          />
        </div>
        <div>
          <TextField
            label="Code postal"
            name="postalCode"
            error={error && error.postalCode}
            onChange={handleChange}
            value={formData.postalCode}
            disabled={isLoading}
          />
          {hasCountryField === false ? (
            <CountryToggle
              type="button"
              onClick={showCountryField}
              disabled={isLoading}
            >
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
              disabled={isLoading}
            />
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
              <Link route="legal" target="_blank" rel="noopener noreferrer">
                politique de conservation des données
              </Link>
            </>
          }
          value={rgpdChecked}
          onChange={handleRgpdCheck}
          disabled={isLoading}
          error={error.rgpd}
        />

        <CheckboxField
          name="moralAgreement"
          label={
            <>
              Action populaire est le réseau social d'action de la France
              insoumise. En m'inscrivant, je m'engage à en respecter{" "}
              <Link route="principes" target="_blank" rel="noopener noreferrer">
                les Principes
              </Link>
              ,{" "}
              <Link
                route="fonctionnement"
                target="_blank"
                rel="noopener noreferrer"
              >
                le fonctionnement
              </Link>{" "}
              et{" "}
              <Link
                route="avenir-en-commun"
                target="_blank"
                rel="noopener noreferrer"
              >
                le programme
              </Link>
              .
            </>
          }
          value={moralAgreementChecked}
          onChange={handleMoralAgreementCheck}
          disabled={isLoading}
          error={error.moralAgreement}
        />
      </div>

      {error && !!error.agreements && (
        <StaticToast>{error.agreements}</StaticToast>
      )}
      {error && !!error.global && <StaticToast>{error.global}</StaticToast>}

      <Button
        type="submit"
        color="primary"
        style={{ marginTop: "2rem" }}
        block
        loading={isLoading}
        disabled={isLoading}
      >
        {location.state?.from === "event"
          ? "Je participe !"
          : "Créer mon compte"}
      </Button>
    </form>
  );
};

export default SignUp;
