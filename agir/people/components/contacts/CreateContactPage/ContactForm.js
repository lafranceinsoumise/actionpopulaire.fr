import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import DateTimeField from "@agir/front/formComponents/DateTimeField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import RadioField from "@agir/front/formComponents/RadioField";
import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";
import TextField from "@agir/front/formComponents/TextField";

import HowTo from "./HowTo";
import NoGroupCard from "./NoGroupCard";

import { searchGroups } from "@agir/groups/utils/api";
import { scrollToError } from "@agir/front/app/utils";
import { getISELink } from "@agir/elections/Common/utils";

const GENDER_OPTIONS = [
  { value: "F", label: "Femme" },
  { value: "M", label: "Homme" },
];

const MEDIA_PREFERENCE_OPTIONS = [
  { value: "media__email", label: "E-mail" },
  { value: "media__whatsapp", label: "WhatsApp" },
  // { value: "media__telegram", label: "Telegram" },
  { value: "media__sms", label: "SMS" },
  { value: "media__courrier", label: "Courrier" },
];

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
    margin: 0;
  }

  h4 {
    font-weight: 600;
    font-size: 1rem;
    margin: 0 0 0.5rem;
  }

  p {
    font-size: 0.875rem;
  }

  em {
    font-weight: 400;
    font-style: italic;
    font-size: 0.875rem;
  }
`;

const formatGroupOptions = (groups) =>
  Array.isArray(groups) && groups.length > 0
    ? groups.map((group) => ({
        ...group,
        icon: "users",
        value: group.id,
        label: group.name,
      }))
    : null;

export const ContactForm = (props) => {
  const { initialData, errors, isLoading, onSubmit, groups } = props;
  const [data, setData] = useState({
    firstName: "",
    lastName: "",
    zip: "",
    email: "",
    phone: "",
    subscribed: true,
    isLiaison: false,
    mediaPreferences: [],
    ...(initialData || {}),
  });
  const [groupOptions, setGroupOptions] = useState(formatGroupOptions(groups));
  const [today] = useState(new Date().toISOString().slice(0, 10));

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

  const handleChangeGender = useCallback((gender) => {
    setData((state) => ({
      ...state,
      gender,
    }));
  });

  const handleChangeBirthDate = useCallback(
    (birthDate) => {
      birthDate = birthDate && birthDate.slice(0, 10);
      birthDate = birthDate < today ? birthDate : null;
      setData((state) => ({
        ...state,
        birthDate,
      }));
    },
    [today],
  );

  const handleCheckLiaison = useCallback((e) => {
    const { checked } = e.target;
    setData((state) => {
      const newState = { ...state };
      newState.isLiaison = checked;
      newState["address"] = checked ? "" : undefined;
      newState["city"] = checked ? "" : undefined;
      newState["country"] = checked ? "FR" : undefined;

      return newState;
    });
  }, []);

  const handleSelectGroup = useCallback(
    (group) => {
      setData((state) => ({
        ...state,
        group,
      }));
      setGroupOptions(formatGroupOptions(groups));
    },
    [groups],
  );

  const handleSelectCountry = useCallback((country) => {
    setData((state) => ({
      ...state,
      country,
    }));
  }, []);

  const handleSearchGroup = useCallback(
    async (searchTerms) => {
      let results = formatGroupOptions(groups);
      if (!searchTerms) {
        setGroupOptions(results);
        return results;
      }
      if (searchTerms.length < 3) {
        setGroupOptions(null);
        return results;
      }
      setGroupOptions(undefined);
      const response = await searchGroups(searchTerms);
      results = formatGroupOptions(response.data?.results);
      setGroupOptions(results);
      return results;
    },
    [groups],
  );

  const handleCheckMediaPreferences = useCallback(
    (e) => {
      const { value, checked } = e.target;
      if (checked && !data.mediaPreferences.includes(value)) {
        setData((state) => ({
          ...state,
          mediaPreferences: [...data.mediaPreferences, value],
        }));
      }
      if (!checked && data.mediaPreferences.includes(value)) {
        setData((state) => ({
          ...state,
          mediaPreferences: data.mediaPreferences.filter((mp) => mp !== value),
        }));
      }
    },
    [data.mediaPreferences],
  );

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      onSubmit({
        ...data,
        group:
          data.hasGroupNotifications && data.group ? data.group : undefined,
      });
    },
    [onSubmit, data],
  );

  useEffect(() => {
    scrollToError(errors, window, 100);
  }, [errors]);

  useEffect(() => {
    !data.group &&
      Array.isArray(groupOptions) &&
      groupOptions.length > 0 &&
      setData((state) => ({
        ...state,
        group: groupOptions[0],
      }));
  }, [groupOptions, data.group]);

  return (
    <StyledForm autoComplete="off" onSubmit={handleSubmit}>
      <h2>Ajouter un contact</h2>
      <HowTo />
      <Spacer size="1.5rem" />
      {!groupOptions && (
        <>
          <NoGroupCard />
          <Spacer size="1.5rem" />
        </>
      )}
      <h3>Informations personnelles</h3>
      <Spacer size="0.5rem" />
      <em>
        &laquo;&nbsp;Souhaitez-vous nous laisser votre
        contact&nbsp;?&nbsp;&raquo;
      </em>
      <Spacer data-scroll="firstName" size="1.5rem" />
      <TextField
        label="Prénom (obligatoire)"
        name="firstName"
        placeholder=""
        onChange={handleChange}
        value={data.firstName}
        disabled={isLoading}
        error={errors?.firstName}
      />
      <Spacer data-scroll="lastName" size="1rem" />
      <TextField
        label="Nom (obligatoire)"
        name="lastName"
        placeholder=""
        onChange={handleChange}
        value={data.lastName}
        disabled={isLoading}
        error={errors?.lastName}
      />
      <Spacer data-scroll="zip" size="1rem" />
      <TextField
        label="Code postal (obligatoire)"
        id="zip"
        error={errors?.zip}
        name="zip"
        placeholder=""
        onChange={handleChange}
        value={data.zip}
        disabled={isLoading}
      />
      <Spacer data-scroll="birthDate" size="1rem" />
      <DateTimeField
        required
        type="date"
        disabled={isLoading}
        id="birthDate"
        name="birthDate"
        value={data.birthDate || null}
        onChange={handleChangeBirthDate}
        error={errors?.birthDate}
        label="Date de naissance"
        autoComplete="birthday"
        helpText={
          <em>
            Facultatif mais utile pour la vérification de l'inscription sur les
            listes électorales
          </em>
        }
      />
      <Spacer data-scroll="birthDate" size="1rem" />
      <RadioField
        disabled={isLoading}
        id="gender"
        name="gender"
        value={data.gender}
        onChange={handleChangeGender}
        error={errors?.gender}
        label="Genre à l'état civil"
        options={GENDER_OPTIONS}
        helpText={
          <em>
            Facultatif mais utile pour la vérification de l'inscription sur les
            listes électorales
          </em>
        }
      />
      <Spacer size="1rem" />
      <Button
        link
        block
        wrap
        href={getISELink(data)}
        target="_blank"
        icon="external-link"
        color="secondary"
      >
        Vérifier l'inscription sur les listes électorales
      </Button>
      <Spacer size="3rem" />
      <h3>Informations de contact</h3>
      <Spacer size="0.5rem" />
      <p>
        Il est <strong>obligatoire</strong> de fournir soit l'adresse e-mail
        soit le téléphone, mais il est vivement recommandé de renseigner les
        deux pour une meilleure expérience.
      </p>
      <Spacer data-scroll="email" size="1rem" />
      <TextField
        label="E-mail"
        id="email"
        error={errors?.email}
        name="email"
        placeholder=""
        onChange={handleChange}
        value={data.email}
        disabled={isLoading}
        type="email"
      />
      <Spacer data-scroll="phone" size="1rem" />
      <PhoneField
        label="Téléphone mobile"
        id="phone"
        name="phone"
        error={errors?.phone}
        onChange={handleChange}
        value={data.phone}
        disabled={isLoading}
        helpText={<em>Facultatif si une adresse e-mail a été renseignée</em>}
      />
      <Spacer data-scroll="subscribed" size="2rem" />
      <h4>Souhaitez-vous recevoir&nbsp;:</h4>
      <CheckboxField
        label="Les informations de la France insoumise"
        onChange={handleCheck}
        value={data.subscribed}
        id="subscribed"
        name="subscribed"
        disabled={isLoading}
      />
      <Spacer data-scroll="group" size=".5rem" />
      <CheckboxField
        label="L'actualité du groupe d'action près de chez vous"
        onChange={handleCheck}
        value={data.hasGroupNotifications}
        id="hasGroupNotifications"
        name="hasGroupNotifications"
        disabled={isLoading}
      />
      <Spacer size="1rem" />
      <SearchAndSelectField
        label="Groupe auquel ajouter le contact"
        placeholder="Choisissez un groupe d'action"
        onChange={handleSelectGroup}
        onSearch={handleSearchGroup}
        isLoading={typeof groupOptions === "undefined"}
        value={data.group}
        id="group"
        name="group"
        defaultOptions={groupOptions}
        error={errors?.group}
        disabled={isLoading || !data.hasGroupNotifications}
      />
      <Spacer size="2rem" />
      <h4>
        Quels sont les moyens de communication que vous utilisez le plus
        souvent&nbsp;?
      </h4>
      <Spacer data-scroll="mediaPreferences" size=".5rem" />
      {MEDIA_PREFERENCE_OPTIONS.map((option) => (
        <CheckboxField
          key={option.value}
          toggle
          label={option.label}
          onChange={handleCheckMediaPreferences}
          value={data.mediaPreferences.includes(option.value)}
          id={option.value}
          inputValue={option.value}
          disabled={isLoading}
        />
      ))}
      <Spacer size="2rem" />
      <h4>
        Souhaitez-vous devenir un &laquo;&nbsp;relai
        insoumis&nbsp;&raquo;&nbsp;?
      </h4>
      <p>
        <em>
          &laquo;&nbsp;Nous vous enverrons des informations ou du matériel pour
          diffuser nos propositions et actions auprès de vos proches et vos
          contacts&nbsp;&raquo;
        </em>
      </p>
      <Spacer size=".5rem" />
      <CheckboxField
        label="Devenir « relai insoumis »"
        onChange={handleCheckLiaison}
        value={data.isLiaison}
        id="isLiaison"
        name="isLiaison"
        disabled={isLoading}
      />
      {data.isLiaison && (
        <>
          <Spacer data-scroll="address" size="1rem" />
          <TextField
            label="Numéro et nom de la rue"
            helpText={
              <em>
                Pour pouvoir vous envoyer des informations en tant que relai
                insoumis
              </em>
            }
            id="address"
            name="address"
            error={errors?.address}
            placeholder=""
            onChange={handleChange}
            value={data.address}
            disabled={isLoading}
          />
          <Spacer data-scroll="city" size="1rem" />
          <TextField
            label="Nom de la commune"
            id="city"
            name="city"
            error={errors?.city}
            placeholder=""
            onChange={handleChange}
            value={data.city}
            disabled={isLoading}
          />
          <Spacer data-scroll="country" size="1rem" />
          <CountryField
            label="Pays"
            id="country"
            name="country"
            error={errors?.country}
            placeholder=""
            onChange={handleSelectCountry}
            value={data.country}
            disabled={isLoading}
          />
          <Spacer size="1rem" />
        </>
      )}
      <Spacer data-scroll="global" size="1.5rem" />
      {errors && errors.global && (
        <p
          css={`
            padding: 0 0 1rem;
            margin: 0;
            font-size: 1rem;
            text-align: center;
            color: ${({ theme }) => theme.error500};
          `}
        >
          {errors.global}
        </p>
      )}
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
