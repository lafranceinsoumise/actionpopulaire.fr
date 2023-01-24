import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import { patchEventSpeakerRequest } from "@agir/event_requests/common/api";
import { useToast } from "@agir/front/globalContext/hooks";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import RadioField from "@agir/front/formComponents/RadioField";

const StyledForm = styled.form`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 1rem;
  flex-flow: row nowrap;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    gap: 0.5rem;
    padding: 0 0.5rem;
  }

  & > * {
    flex: 0 0 auto;
  }

  & > :nth-child(2) {
    flex: 1 1 auto;
  }
`;

const AVAILABLE_FIELD_OPTIONS = [
  { label: "Disponible", value: "1" },
  { label: "Non disponible", value: "0" },
];

const EventSpeakerRequestForm = (props) => {
  const [isLoading, setIsLoading] = useState(false);
  const [request, setRequest] = useState({ ...props });
  const [hasChanged, setHasChanged] = useState(false);
  const [isNew, setIsNew] = useState(request.available === null);

  const sendToast = useToast();

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setIsLoading(true);
      const result = await patchEventSpeakerRequest(request);
      setIsLoading(false);
      if (result.error) {
        sendToast("Une erreur est survenue. Veuillez ressayer.", "ERROR", {
          autoClose: true,
        });
        return;
      }
      sendToast("Informations mises à jour", "SUCCESS", {
        autoClose: true,
      });
      result.data && setRequest(result.data);
      setHasChanged(false);
      setIsNew(false);
    },
    [sendToast, request]
  );

  const handleChangeAvailable = useCallback((value) => {
    setHasChanged(true);
    setRequest((state) => ({ ...state, available: Boolean(parseInt(value)) }));
  }, []);

  const handleChangeComment = useCallback((e) => {
    setHasChanged(true);
    setRequest((state) => ({ ...state, comment: e.target.value }));
  }, []);

  return (
    <StyledForm onSubmit={handleSubmit}>
      <RadioField
        small
        id={request.id + "_available"}
        value={
          request.available === null ? null : String(Number(request.available))
        }
        onChange={handleChangeAvailable}
        options={AVAILABLE_FIELD_OPTIONS}
        required
      />
      <TextField
        small
        id={request.id + "_comment"}
        label=""
        placeholder="Commentaire"
        aria-label="Commentaire"
        value={request.comment}
        onChange={handleChangeComment}
        maxLength={255}
        hasCounter={false}
      />
      <Button
        small
        icon={isNew || hasChanged ? "" : "check"}
        color={isNew || hasChanged ? "primary" : "secondary"}
        type="submit"
        loading={isLoading}
        disabled={isLoading || !hasChanged}
      >
        {!isNew && !hasChanged
          ? "Enregistré"
          : isNew
          ? "Enregistrer"
          : "Mettre à jour"}
      </Button>
    </StyledForm>
  );
};
EventSpeakerRequestForm.propTypes = {
  id: PropTypes.string.isRequired,
  available: PropTypes.bool,
  comment: PropTypes.string,
};

export default EventSpeakerRequestForm;
