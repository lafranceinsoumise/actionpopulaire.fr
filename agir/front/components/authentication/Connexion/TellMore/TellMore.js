import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { Hide } from "@agir/front/genericComponents/grid";
import PhoneField from "@agir/front/formComponents/PhoneField";
import SelectField from "@agir/front/formComponents/SelectField";
import TextField from "@agir/front/formComponents/TextField";

import { updateProfile, getProfile } from "@agir/front/authentication/api";

import helloDesktop from "@agir/front/genericComponents/images/hello-desktop.svg";

const LeftBlock = styled.div`
  width: 40%;
  height: 100vh;
  display: flex;
  position: relative;
  align-items: center;
  justify-content: flex-end;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainBlock = styled.div`
  width: 60%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  font-size: 13px;
  padding: 32px;

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    align-items: center;
  }

  input {
    border-color: #c4c4c4;
  }

  label {
    font-weight: 600;
  }

  h1 {
    margin: 0px;
    font-weight: 700;
    font-size: 2rem;
  }

  h2 {
    font-size: 1rem;
    line-height: 24px;
    font-weight: 400;
    margin-bottom: 40px;
    margin-top: 0;
  }
`;

const InputGroup = styled.div`
  display: inline-flex;
  justify-content: space-between;
  width: 100%;

  > div:nth-child(1) {
    width: 155px;
  }

  > div:nth-child(2) {
    width: 346px;
  }

  @media (max-width: ${style.collapse}px) {
    display: block;

    > div:nth-child(1) {
      width: 100%;
    }

    > div:nth-child(2) {
      width: 100%;
    }
  }
`;

const DEFAULT_DATA = {
  displayName: "",
  firstName: "",
  lastName: "",
  contactPhone: "",
  zip: "",
  mandat: null,
};
const MANDAT_OPTIONS = [
  {
    label: "Mandat municipal",
    value: "municipal",
  },
  {
    label: "Mandat départemental",
    value: "departemental",
  },
  {
    label: "Mandat régional",
    value: "regional",
  },
];

const TellMore = ({ dismiss }) => {
  const [formData, setFormData] = useState(DEFAULT_DATA);
  const [existantData, setExistantData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState({});

  const getProfileInfos = useCallback(async () => {
    setIsLoading(true);
    const { data } = await getProfile();
    setIsLoading(false);
    setFormData({
      displayName:
        data.displayName?.length > 2
          ? data.displayName
          : DEFAULT_DATA.displayName,
      firstName: data.firstName || DEFAULT_DATA.firstName,
      lastName: data.lastName || DEFAULT_DATA.lastName,
      contactPhone: data.contactPhone || DEFAULT_DATA.contactPhone,
      zip: data.zip || DEFAULT_DATA.zip,
      mandat:
        Array.isArray(data.mandat) && data.mandat.length > 0
          ? data.mandat[0]
          : null,
    });
    setExistantData({ firstName: !!data.firstName, lastName: !!data.lastName });
  }, []);

  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((formData) => ({
      ...formData,
      [name]: value,
    }));
  }, []);

  const toggleShowMandat = useCallback(() => {
    setFormData((formData) => ({
      ...formData,
      mandat: formData.mandat ? null : MANDAT_OPTIONS[0].value,
    }));
  }, []);

  const handleChangeMandat = useCallback((option) => {
    setFormData((formData) => ({ ...formData, mandat: option.value }));
  }, []);

  const handleSubmit = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    const data = await updateProfile(formData);
    setIsLoading(false);
    if (data.error) {
      setError(data.error);
      return;
    }
    dismiss();
  }, [dismiss, formData]);

  useEffect(() => {
    getProfileInfos();
  }, [getProfileInfos]);

  return (
    <div style={{ display: "flex" }}>
      <LeftBlock>
        <img
          src={helloDesktop}
          alt="Bienvenue"
          style={{ width: "220px", paddingRight: "60px" }}
        />
      </LeftBlock>
      <MainBlock>
        <div style={{ width: "100%", maxWidth: "517px" }}>
          <h1>Je complète mon profil</h1>
          <h2>Complétez les informations vous concernant</h2>
          <label style={{ marginBottom: "0" }}>Nom public</label> (obligatoire)
          <br />
          <span>
            Le nom que pourrons voir les membres avec qui vous interagissez.
            Indiquez par exemple votre prénom ou un pseudonyme.
          </span>
          <TextField
            error={error && error.displayName}
            name="displayName"
            placeholder="Mathilde P."
            onChange={handleInputChange}
            value={formData.displayName}
            disabled={isLoading}
          />
          {existantData?.firstName && (
            <TextField
              label={
                <>
                  Prénom <span style={{ fontWeight: 400 }}>(facultatif)</span>
                </>
              }
              name="firstName"
              placeholder=""
              onChange={handleInputChange}
              value={formData.firstName}
              disabled={isLoading}
            />
          )}
          {existantData?.firstName && (
            <TextField
              label={
                <>
                  Nom <span style={{ fontWeight: 400 }}>(facultatif)</span>
                </>
              }
              id="lastName"
              name="lastName"
              placeholder=""
              onChange={handleInputChange}
              value={formData.lastName}
              disabled={isLoading}
            />
          )}
          <InputGroup>
            <div>
              <TextField
                label="Code postal"
                id="zip"
                error={error && error.zip}
                name="zip"
                placeholder=""
                onChange={handleInputChange}
                value={formData.zip}
                disabled={isLoading}
              />
            </div>
            <div>
              <PhoneField
                label={
                  <>
                    Numéro de téléphone{" "}
                    <span style={{ fontWeight: 400 }}>(facultatif)</span>
                  </>
                }
                id="contactPhone"
                name="contactPhone"
                error={error && error.contactPhone}
                onChange={handleInputChange}
                value={formData.contactPhone}
                disabled={isLoading}
              />
            </div>
          </InputGroup>
          <div style={{ marginTop: "0.625rem" }}>
            <CheckboxField
              name="mandat"
              label="Je suis élu·e"
              value={formData.mandat !== null}
              onChange={toggleShowMandat}
              disabled={isLoading}
            />
          </div>
          {formData.mandat !== null && (
            <div style={{ marginTop: "10px" }}>
              <SelectField
                label="Mandat"
                name="mandat"
                value={MANDAT_OPTIONS.find(
                  (option) => option.value === formData.mandat
                )}
                options={MANDAT_OPTIONS}
                onChange={handleChangeMandat}
                disabled={isLoading}
              />
            </div>
          )}
          <Button
            color="primary"
            onClick={handleSubmit}
            disabled={isLoading}
            style={{
              width: "356px",
              maxWidth: "100%",
              marginTop: "1rem",
              marginBottom: "2rem",
              justifyContent: "center",
            }}
          >
            Enregistrer
          </Button>
          {formData.mandat === null && (
            <Hide under style={{ paddingBottom: "79px" }}></Hide>
          )}
        </div>
      </MainBlock>
    </div>
  );
};

TellMore.propTypes = {
  dismiss: PropTypes.func.isRequired,
};
export default TellMore;
