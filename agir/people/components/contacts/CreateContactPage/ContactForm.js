import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import CountryField from "@agir/front/formComponents/CountryField";
import PhoneField from "@agir/front/formComponents/PhoneField";
import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";
import TextField from "@agir/front/formComponents/TextField";

import HowTo from "./HowTo";
import NoGroupCard from "./NoGroupCard";

import { searchGroups } from "@agir/groups/utils/api";
import { scrollToError } from "@agir/front/app/utils";

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
    margin: 0;
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

const formatGroupOptions = (groups) =>
  Array.isArray(groups) && groups.length > 0
    ? [
        ...groups.map((group) => ({
          ...group,
          icon: "users",
          value: group.id,
          label: group.name,
        })),
        {
          id: null,
          value: "",
          label: "Ne pas ajouter à un groupe",
        },
      ]
    : null;

export const ContactForm = (props) => {
  const { initialData, errors, isLoading, onSubmit, groups } = props;
  const [data, setData] = useState({
    firstName: "",
    lastName: "",
    zip: "",
    email: "",
    phone: "",
    isPoliticalSupport: true,
    newsletters: ["2022_exceptionnel"],
    ...(initialData || {}),
  });
  const [groupOptions, setGroupOptions] = useState(formatGroupOptions(groups));

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

  const handleCheckisPoliticalSupport = useCallback((e) => {
    const { checked } = e.target;
    setData((state) => ({
      ...state,
      isPoliticalSupport: checked,
      newsletters: checked
        ? state.newsletters
        : state.newsletters.filter((nl) => nl !== NEWSLETTER_2022_LIAISON),
      address: checked ? state.address : undefined,
      city: checked ? state.city : undefined,
      country: checked ? state.country : undefined,
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
      hasGroupNotifications: group?.id
        ? state.hasGroupNotifications
        : undefined,
      group,
    }));
    setGroupOptions(formatGroupOptions(groups));
  }, []);

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
    [groupOptions]
  );

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      onSubmit(data);
    },
    [onSubmit, data]
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
      <h3>Nouveau contact</h3>
      <Spacer size="0.5rem" />
      <em>
        &laquo;&nbsp;Souhaitez-vous nous laisser votre
        contact&nbsp;?&nbsp;&raquo;
      </em>
      <Spacer data-scroll="firstName" size="1.5rem" />
      <TextField
        label="Prénom*"
        name="firstName"
        placeholder=""
        onChange={handleChange}
        value={data.firstName}
        disabled={isLoading}
        error={errors?.firstName}
      />
      <Spacer data-scroll="lastName" size="1rem" />
      <TextField
        label="Nom*"
        name="lastName"
        placeholder=""
        onChange={handleChange}
        value={data.lastName}
        disabled={isLoading}
        error={errors?.lastName}
      />
      <Spacer data-scroll="zip" size="1rem" />
      <TextField
        label="Code postal*"
        id="zip"
        error={errors?.zip}
        name="zip"
        placeholder=""
        onChange={handleChange}
        value={data.zip}
        disabled={isLoading}
      />
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
      <Spacer data-scroll="newsletters" size="2rem" />
      <h4>
        &laquo;&nbsp;Souhaitez-vous rejoindre la France
        insoumise&nbsp;?&nbsp;&raquo;
      </h4>
      <CheckboxField
        label="Je veux rejoindre la France insoumise"
        onChange={handleCheckisPoliticalSupport}
        value={data.isPoliticalSupport}
        id="isPoliticalSupport"
        name="isPoliticalSupport"
        disabled={isLoading}
      />
      <Spacer data-scroll="newsletters" size="1.5rem" />
      <h4>Souhaitez-vous recevoir les&nbsp;:</h4>
      <CheckboxField
        label={
          <>
            Informations très importantes et exceptionnelles
            <br />
            <em>
              &laquo;&nbsp;Un grand meeting ou une action importante est
              organisée dans votre ville ou près de chez vous&nbsp;&raquo;
            </em>
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
        label={
          <>
            Informations des campagnes de la France insoumise
            <br />
            <em>
              &laquo;&nbsp;Les lettres d'informations concernants les actions et
              l'actualité du mouvement&nbsp;&raquo;
            </em>
          </>
        }
        onChange={handleCheckNewsletter}
        value={data.newsletters.includes("2022")}
        id="2022"
        name="2022"
        disabled={isLoading}
      />
      <Spacer data-scroll="group" size="1.5rem" />
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
        disabled={isLoading}
      />
      {data.group?.id && (
        <>
          <Spacer size=".5rem" />
          <CheckboxField
            label="Je veux recevoir les actualités du groupe"
            onChange={handleCheck}
            value={data.hasGroupNotifications}
            id="hasGroupNotifications"
            name="hasGroupNotifications"
            disabled={isLoading}
          />
        </>
      )}
      {data.isPoliticalSupport && (
        <>
          <Spacer size="1.5rem" />
          <h4>
            Souhaitez-vous devenir correspondant·e pour votre immeuble ou votre
            village&nbsp;?
          </h4>
          <p>
            <em>
              &laquo;&nbsp;Nous vous enverrons des informations et du matériel
              pour diffuser nos propositions et actions auprès de vos voisins et
              voisines&nbsp;&raquo;
            </em>
          </p>
          <Spacer size=".5rem" />
          <CheckboxField
            label="Devenir correspondant·e de l'immeuble ou du village"
            onChange={handleCheckNewsletter}
            value={data.newsletters.includes(NEWSLETTER_2022_LIAISON)}
            id={NEWSLETTER_2022_LIAISON}
            name={NEWSLETTER_2022_LIAISON}
            disabled={isLoading}
          />
        </>
      )}
      {data.newsletters.includes(NEWSLETTER_2022_LIAISON) && (
        <>
          <Spacer data-scroll="address" size="1rem" />
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
          />
          <Spacer data-scroll="city" size="1rem" />
          <TextField
            label="Nom de la ville"
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
            color: ${({ theme }) => theme.redNSP};
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
