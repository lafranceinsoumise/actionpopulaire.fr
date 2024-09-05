import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { usePrevious } from "react-use";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import FileField from "@agir/front/formComponents/FileField";
import TextField from "@agir/front/formComponents/TextField";

import { EVENT_DOCUMENT_TYPES } from "./config";

const StyledIconButton = styled.button`
  border: none;
  padding: 0;
  margin: 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${(props) => props.theme.text1000};

  span {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    height: 2rem;
    width: 2rem;
  }
`;

const StyledHeader = styled.header`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-gap: 0 1rem;
  align-items: center;
  padding: 0 1.5rem;
  height: 54px;
  font-weight: 600;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    position: sticky;
    top: 0;
    height: 64px;
    background-color: ${(props) => props.theme.background0};
    z-index: 1;
  }

  h4 {
    font-weight: 600;
    font-size: 1rem;
    line-height: 2rem;
    grid-column: 1/3;
    grid-row: 1/2;
    text-align: center;
  }

  ${StyledIconButton} {
    grid-column: 2/3;
    grid-row: 1/2;
  }
`;

const StyledForm = styled.form`
  padding: 1.5rem;
  min-height: 200px;

  && input,
  && textarea {
    border-radius: ${(props) => props.theme.borderRadius};
  }
`;

const StyledModalContent = styled.div`
  max-width: 600px;
  margin: 40px auto;
  background-color: ${(props) => props.theme.background0};
  border-radius: ${(props) => props.theme.borderRadius};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    border-radius: 0;
    max-width: 100%;
    min-height: 100vh;
    padding-bottom: 1.5rem;
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
  }

  ${StyledHeader} {
    border-bottom: ${(props) =>
      props.$isLoading
        ? `8px solid ${props.theme.secondary500}`
        : `1px solid ${props.theme.text100};`};
    transition: border-bottom 250ms ease-in-out;
  }

  ${StyledForm} {
    opacity: ${({ $isLoading }) => ($isLoading ? ".3" : "1")};
    transition: opacity 250ms ease-in-out;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
    }
  }
`;

const INITIAL_DATA = (type) => ({
  file: null,
  name: EVENT_DOCUMENT_TYPES[type]?.name || "",
  description: "",
});

const RequiredDocumentModal = (props) => {
  const { type, shouldShow, isLoading, onClose, onSubmit, errors } = props;

  const [data, setData] = useState({ ...INITIAL_DATA(type) });
  const wasLoading = usePrevious(isLoading);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ type, ...data });
  };

  const maySubmit = !isLoading && !!data?.file && !!data?.name;

  useEffect(() => {
    !!type && setData({ ...INITIAL_DATA(type) });
  }, [type]);

  useEffect(() => {
    if (wasLoading && !isLoading && !errors) {
      onClose();
    }
  }, [isLoading, wasLoading, errors, onClose]);

  return (
    <Modal
      shouldShow={shouldShow}
      onClose={isLoading ? undefined : onClose}
      noScroll
    >
      <StyledModalContent $isLoading={isLoading}>
        <StyledHeader>
          <h4>Nouveau document</h4>
          <StyledIconButton
            type="button"
            onClick={onClose}
            disabled={isLoading}
          >
            <RawFeatherIcon name="x" />
          </StyledIconButton>
        </StyledHeader>
        <StyledForm onSubmit={handleSubmit}>
          <FileField
            id="file"
            name="file"
            value={data.file}
            onChange={(file) => setData({ ...data, file })}
            label="Télécharger le document"
            helpText="Formats autorisés : .PDF .PNG .JPG .DOCX"
            accept=".pdf,.png,.jpg,.jpeg,.docx"
            error={errors?.file}
          />
          <Spacer size="1.25rem" />
          <TextField
            label="Nom du document"
            placeholder="Ex : prêt de retro-projecteur"
            id="name"
            name="name"
            value={data.name}
            onChange={(e) => setData({ ...data, name: e.target.value })}
            isLoading={isLoading}
            disabled={isLoading}
            error={errors?.name}
            required
          />
          <Spacer size="1.25rem" />
          <TextField
            label={
              <>
                Détails du document{" "}
                <span style={{ fontWeight: 400 }}>(facultatif)</span>
              </>
            }
            id="description"
            name="description"
            value={data.description}
            onChange={(e) => setData({ ...data, description: e.target.value })}
            isLoading={isLoading}
            disabled={isLoading}
            textArea={true}
            rows={4}
            error={errors?.description}
          />
          <Spacer size="2rem" />
          <Button disabled={!maySubmit} type="submit" color="secondary">
            Envoyer le document
          </Button>
        </StyledForm>
      </StyledModalContent>
    </Modal>
  );
};

RequiredDocumentModal.propTypes = {
  type: PropTypes.string,
  shouldShow: PropTypes.bool,
  isLoading: PropTypes.bool,
  onClose: PropTypes.func,
  onSubmit: PropTypes.func.isRequired,
  errors: PropTypes.object,
};

export default RequiredDocumentModal;
