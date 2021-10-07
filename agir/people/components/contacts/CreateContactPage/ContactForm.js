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

const scrollToError = (errors) => {
  if (
    typeof window === "undefined" ||
    !errors ||
    Object.values(errors).filter(Boolean).length === 0
  ) {
    return;
  }
  const keys = Object.entries(errors)
    .filter(([_, value]) => Boolean(value))
    .map(([key]) => key);
  let scrollTarget = null;
  for (let i = 0; keys[0] && !scrollTarget; i += 1) {
    scrollTarget = document.querySelector(`[data-scroll="${keys[0]}"]`);
  }
  if (!scrollTarget) {
    return;
  }
  const rect = scrollTarget.getBoundingClientRect();
  const isVisible =
    rect.top - 100 >= 0 &&
    rect.bottom + 100 <=
      (window.innerHeight || document.documentElement.clientHeight);

  !isVisible &&
    window.scrollTo({
      top: scrollTarget.offsetTop - 100,
    });
};

export const ContactForm = (props) => {
  const { initialData, errors, isLoading, onSubmit, groups } = props;

  const [data, setData] = useState({
    firstName: "",
    lastName: "",
    zip: "",
    email: "",
    phone: "",
    is2022: true,
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

  const handleCheckIs2022 = useCallback((e) => {
    const { checked } = e.target;
    setData((state) => ({
      ...state,
      is2022: checked,
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
        ? [
            ...groups.map((group) => ({
              ...group,
              value: group.id,
              label: group.name,
            })),
            {
              id: null,
              value: "",
              label: "Ne pas ajouter à un groupe",
            },
          ]
        : null,
    [groups]
  );

  useEffect(() => {
    scrollToError(errors);
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
        label="Prénom"
        name="firstName"
        placeholder=""
        onChange={handleChange}
        value={data.firstName}
        disabled={isLoading}
        required={false}
        error={errors?.firstName}
      />
      <Spacer data-scroll="lastName" size="1rem" />
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
      <Spacer data-scroll="zip" size="1rem" />
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
        required={false}
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
        helpText={
          <em>
            Facultatif mais utile pour vous rappeler d’aller voter avant le 1er
            tour&nbsp;!
          </em>
        }
      />
      <Spacer data-scroll="newsletters" size="2rem" />
      <h4>
        &laquo;&nbsp;Souhaitez-vous compter dans les soutiens de Jean-Luc
        Mélenchon pour 2022&nbsp;?&nbsp;&raquo;
      </h4>
      <CheckboxField
        label="Je veux compter dans les soutiens"
        onChange={handleCheckIs2022}
        value={data.is2022}
        id="is2022"
        name="is2022"
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
              &laquo;&nbsp;Jean-Luc Mélenchon fait un meeting dans votre
              ville&nbsp;&raquo;
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
            Informations de la campagne
            <br />
            <em>
              &laquo;&nbsp;Jean-Luc Mélenchon va passer à la TV la semaine
              prochaine&nbsp;&raquo;
            </em>
          </>
        }
        onChange={handleCheckNewsletter}
        value={data.newsletters.includes("2022")}
        id="2022"
        name="2022"
        disabled={isLoading}
      />
      {groupOptions && (
        <>
          <Spacer data-scroll="group" size="1.5rem" />
          <SelectField
            label="Groupe auquel ajouter le contact"
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
      {data.is2022 ? (
        <>
          <Spacer size="1.5rem" />
          <h4>
            Souhaitez-vous devenir correspondant·e pour votre immeuble ou votre
            rue&nbsp;?
          </h4>
          <p>
            <em>
              &laquo;&nbsp;Nous vous enverrons des informations et du matériel
              pour diffuser nos propositions et inciter vos voisins à aller
              voter pour tout changer en 2022&nbsp;&raquo;
            </em>
          </p>
          <Spacer size=".5rem" />
          <CheckboxField
            label="Devenir correspondant·e de l'immeuble ou de la rue"
            onChange={handleCheckNewsletter}
            value={data.newsletters.includes(NEWSLETTER_2022_LIAISON)}
            id={NEWSLETTER_2022_LIAISON}
            name={NEWSLETTER_2022_LIAISON}
            disabled={isLoading}
          />
        </>
      ) : null}
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
            required={false}
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
            required={false}
          />
          <Spacer data-scroll="country" size="1rem" />
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
