import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import SelectField from "@agir/front/formComponents/SelectField";
import TextField from "@agir/front/formComponents/TextField";

import HowTo from "./HowTo";
import NoGroupCard from "./NoGroupCard";
import { StepTitle } from "./StyledComponents";

const NEWSLETTER_2022_LIAISON = "2022_liaison";

const StyledForm = styled.form`
  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    margin: 0 0 1.5rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }

  h3 {
    font-weight: 700;
    font-size: 1.25rem;
    margin: 0 0 1.5rem;
  }

  h4 {
    font-weight: 600;
    font-size: 1rem;
    margin: 0 0 0.5rem;
  }

  em {
    font-weight: 400;
    font-style: italic;
    font-size: 0.875rem;
  }
`;

export const ContactForm = (props) => {
  const { initialData, errors, isLoading, onSubmit, groups } = props;

  const [data, setData] = useState({
    firstName: "",
    lastName: "",
    zip: "",
    email: "",
    phone: "",
    newsletters: ["2022_exceptionnel"],
    ...(initialData || {}),
  });

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setData((state) => ({
      ...state,
      [name]: value,
    }));
  }, []);

  const handleCheck = useCallback((e) => {
    const { name, checked } = e.target;
    setData((state) => ({
      ...state,
      [name]: checked,
    }));
  }, []);

  const handleCheckIsGroupFollower = useCallback((e) => {
    const { checked } = e.target;
    setData((state) => ({
      ...state,
      group: checked ? groupOptions[0] : undefined,
    }));
  }, []);

  const handleCheckNewsletter = useCallback((e) => {
    const { name, checked } = e.target;
    setData((state) => {
      const newState = { ...state };
      newState["newsletters"] = checked
        ? [...state.newsletters, name]
        : state.newsletters.filter((nl) => nl !== name);
      if (name === NEWSLETTER_2022_LIAISON) {
        newState["address"] = checked ? "" : undefined;
        newState["city"] = checked ? "" : undefined;
        newState["country"] = checked ? "FR" : undefined;
      }
      return newState;
    });
  }, []);

  const handleSelectGroup = useCallback((group) => {
    setData((state) => ({
      ...state,
      group,
    }));
  }, []);

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      onSubmit(data);
    },
    [onSubmit, data]
  );

  const groupOptions = useMemo(
    () =>
      Array.isArray(groups) && groups.length > 0
        ? groups.map((group) => ({
            value: group.id,
            label: group.name,
          }))
        : null,
    [groups]
  );

  return (
    <StyledForm onSubmit={handleSubmit}>
      <h2>Ajouter un soutien</h2>
      <HowTo />
      <Spacer size="1.5rem" />
      {!groupOptions && (
        <>
          <NoGroupCard />
          <Spacer size="1.5rem" />
        </>
      )}
      <h3>Nouveau soutien</h3>
      <TextField
        label="Prénom"
        name="firstName"
        placeholder=""
        onChange={handleChange}
        value={data.firstName}
        disabled={isLoading}
        required={false}
        error={errors?.firstName}
      />
      <Spacer size="1rem" />
      <TextField
        label="Nom"
        name="lastName"
        placeholder=""
        onChange={handleChange}
        value={data.lastName}
        disabled={isLoading}
        required={false}
        error={errors?.lastName}
      />
      <Spacer size="1rem" />
      <TextField
        label="Code postal"
        id="zip"
        error={errors?.zip}
        name="zip"
        placeholder=""
        onChange={handleChange}
        value={data.zip}
        disabled={isLoading}
        required={false}
      />
      <Spacer size="1rem" />
      <TextField
        label="E-mail"
        id="email"
        error={errors?.email}
        name="email"
        placeholder=""
        onChange={handleChange}
        value={data.email}
        disabled={isLoading}
        required={false}
      />
      <Spacer size="1rem" />
      <PhoneField
        label="Numéro de téléphone"
        id="phone"
        name="phone"
        error={errors?.phone}
        onChange={handleChange}
        value={data.phone}
        disabled={isLoading}
        helpText={
          <em>
            Facultatif mais utile pour vous rappeler d’aller voter avant le 1er
            tour&nbsp;!
          </em>
        }
      />
      <Spacer size="1rem" />
      <h4>Souhaitez-vous recevoir les&nbsp;:</h4>
      <CheckboxField
        label={
          <>
            Informations très importantes et exceptionnelles
            <br />
            <em>« Jean-Luc Mélenchon fait un meeting dans votre ville »</em>
          </>
        }
        onChange={handleCheckNewsletter}
        value={data.newsletters.includes("2022_exceptionnel")}
        id="2022_exceptionnel"
        name="2022_exceptionnel"
        disabled={isLoading}
      />
      <Spacer size=".5rem" />
      <CheckboxField
        label="Informations hebdomadaires"
        onChange={handleCheckNewsletter}
        value={data.newsletters.includes("2022")}
        id="2022"
        name="2022"
        disabled={isLoading}
      />
      {groupOptions && (
        <>
          <Spacer size=".5rem" />
          <CheckboxField
            label="Actualités du groupe d’action"
            onChange={handleCheckIsGroupFollower}
            value={!!data.group}
            id="isGroupFollower"
            name="isGroupFollower"
            disabled={isLoading}
          />
          {data.group && (
            <>
              <Spacer size="1.5rem" />
              <SelectField
                label="Ajouter un contact à quel groupe ?"
                placeholder="Choisissez un groupe d'action"
                onChange={handleSelectGroup}
                value={data.group}
                id="group"
                name="group"
                options={groupOptions}
                error={errors?.group}
                disabled={isLoading}
                required={false}
              />
            </>
          )}
        </>
      )}
      <Spacer size="1.5rem" />
      <h4>
        Souhaitez-vous devenir correspondant·e pour votre immeuble ou votre
        rue&nbsp;?
      </h4>
      <p>
        <em>
          « Nous vous enverrons des informations et du matériel pour diffuser
          nos propositions et inciter vos voisins à aller voter pour tout
          changer en 2022 »
        </em>
      </p>
      <Spacer size=".5rem" />
      <CheckboxField
        label="Devenir correspondant·e"
        onChange={handleCheckNewsletter}
        value={data.newsletters.includes(NEWSLETTER_2022_LIAISON)}
        id={NEWSLETTER_2022_LIAISON}
        name={NEWSLETTER_2022_LIAISON}
        disabled={isLoading}
      />
      {data.newsletters.includes(NEWSLETTER_2022_LIAISON) && (
        <>
          <Spacer size="1rem" />
          <TextField
            label="Numéro et nom de la rue"
            helpText={
              <em>
                Pour pouvoir vous envoyer des informations en tant que
                correspondant·e
              </em>
            }
            id="address"
            name="address"
            error={errors?.address}
            placeholder=""
            onChange={handleChange}
            value={data.address}
            disabled={isLoading}
            required={false}
          />
          <Spacer size="1rem" />
          <TextField
            label="Nom de la ville"
            id="city"
            name="city"
            error={errors?.city}
            placeholder=""
            onChange={handleChange}
            value={data.city}
            disabled={isLoading}
            required={false}
          />
          <Spacer size="1rem" />
          <CountryField
            label="Pays"
            id="country"
            name="country"
            error={errors?.country}
            placeholder=""
            onChange={handleChange}
            value={data.country}
            disabled={isLoading}
            required={false}
          />
          <Spacer size="1rem" />
        </>
      )}
      <Spacer size="1.5rem" />
      <Button block type="submit" color="primary" disabled={isLoading}>
        Suivant
      </Button>
    </StyledForm>
  );
};
ContactForm.propTypes = {
  initialData: PropTypes.object,
  errors: PropTypes.object,
  isLoading: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  groups: PropTypes.arrayOf(PropTypes.object),
};

export default ContactForm;
