import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";
import { mutate } from "swr";

import { updateProfile } from "@agir/front/authentication/api";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import CountryField from "@agir/front/formComponents/CountryField";
import Spacer from "@agir/front/genericComponents/Spacer";
import TextField from "@agir/front/formComponents/TextField";

const StyledModalContent = styled.div`
  position: relative;
  max-width: 600px;
  padding: 2.25rem;
  margin: 60px auto 0;
  box-shadow: ${(props) => props.theme.elaborateShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.white};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin-top: 20px;
    max-width: calc(100% - 40px);
    padding: 1.5rem;
  }

  h4,
  p {
    margin: 0;
  }
`;

export const UpdateAddressModal = (props) => {
  const { shouldShow, isLoading, initialData, errors, onSubmit } = props;

  const [data, setData] = useState({
    address1: initialData?.address1 || "",
    address2: initialData?.address2 || "",
    zip: initialData?.zip || "",
    city: initialData?.city || "",
    country: initialData?.country || "FR",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(data);
  };

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setData((state) => ({
      ...state,
      [name]: value,
    }));
  }, []);

  const handleChangeCountry = useCallback((country) => {
    setData((state) => ({ ...state, country }));
  }, []);

  return (
    <Modal shouldShow={shouldShow} noScroll>
      <StyledModalContent>
        <h4>Localisation</h4>
        <Spacer size=".5rem" />
        <p>
          Entrez votre adresse pour que nous puissions vous suggérer les
          événements à proximité de chez vous.
        </p>
        <Spacer size="1.5rem" />
        <form onSubmit={handleSubmit}>
          <TextField
            label="Adresse"
            id="address1"
            error={errors?.address1}
            name="address1"
            placeholder=""
            onChange={handleChange}
            value={data.address1}
            disabled={isLoading}
          />
          <Spacer size="1rem" />
          <TextField
            label="Complément d'adresse"
            id="address2"
            error={errors?.address2}
            name="address2"
            placeholder=""
            onChange={handleChange}
            value={data.address2}
            disabled={isLoading}
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
          />
          <Spacer size="1rem" />
          <TextField
            label="Commune"
            id="city"
            error={errors?.city}
            name="city"
            placeholder=""
            onChange={handleChange}
            value={data.city}
            disabled={isLoading}
          />
          <Spacer size="1rem" />
          <CountryField
            label="Pays"
            id="country"
            error={errors?.country}
            name="country"
            placeholder=""
            onChange={handleChangeCountry}
            value={data.country}
            disabled={isLoading}
          />
          <Spacer size="1rem" />
          {errors?.global && (
            <p
              css={`
                margin: 0;
                color: ${({ theme }) => theme.redNSP};
                text-align: center;
              `}
            >
              {errors.global}
            </p>
          )}
          <Spacer size="1rem" />
          <Button
            block
            disabled={isLoading}
            loading={isLoading}
            type="submit"
            color="primary"
          >
            Valider
          </Button>
        </form>
      </StyledModalContent>
    </Modal>
  );
};
UpdateAddressModal.propTypes = {
  shouldShow: PropTypes.bool,
  isLoading: PropTypes.bool,
  onSubmit: PropTypes.func,
  errors: PropTypes.shape({
    address1: PropTypes.string,
    address2: PropTypes.string,
    zip: PropTypes.string,
    city: PropTypes.string,
    country: PropTypes.string,
    global: PropTypes.string,
  }),
  initialData: PropTypes.shape({
    address1: PropTypes.string,
    address2: PropTypes.string,
    zip: PropTypes.string,
    city: PropTypes.string,
    country: PropTypes.string,
  }),
};

const ConnectedUpdateAddressModal = (props) => {
  const { shouldShow, onClose, user } = props;
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState(null);

  const handleSubmit = useCallback(
    async (data) => {
      if (!data.zip) {
        setErrors({
          zip: "Ce champ est obligatoire",
          global:
            "Entrez une adresse. Seul le code postal est obligatoire pour continuer.",
        });
        return;
      }
      setErrors(null);
      setIsLoading(true);
      const { error } = await updateProfile(data);
      setIsLoading(false);
      if (error) {
        setErrors(error);
        return;
      }
      mutate("/api/session/", (session) => ({
        ...session,
        user: { ...session.user, zip },
      }));
      onClose && onClose();
    },
    [onClose]
  );

  return (
    <UpdateAddressModal
      shouldShow={shouldShow}
      isLoading={isLoading}
      errors={errors}
      onSubmit={handleSubmit}
      initialData={user}
    />
  );
};

ConnectedUpdateAddressModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  user: PropTypes.shape({
    address1: PropTypes.string,
    address2: PropTypes.string,
    zip: PropTypes.string,
    city: PropTypes.string,
    country: PropTypes.string,
  }),
};

export default ConnectedUpdateAddressModal;
