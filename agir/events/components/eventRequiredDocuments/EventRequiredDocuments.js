import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";

import { dateFromISOString, displayShortDate } from "@agir/lib/utils/time";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import Spacer from "@agir/front/genericComponents/Spacer";

import EventSubtypePicker from "./EventSubtypePicker";
import NoRequiredDocumentCard from "./NoRequiredDocumentCard";
import ProjectStatusCard from "./ProjectStatusCard";
import RequiredDocumentCard from "./RequiredDocumentCard";
import RequiredDocumentModal from "./RequiredDocumentModal";
import SentDocumentsCard from "./SentDocumentsCard";

import { EVENT_DOCUMENT_TYPES } from "./config";

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }

  svg {
    height: 16px;
    width: 16px;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

const StyledDocumentList = styled.div`
  & + & {
    margin-top: 2.5rem;
  }

  & > h4 {
    margin: 0;
    font-weight: 600;
    font-size: 1.125rem;
    line-height: 1.5;
    color: ${(props) =>
      props.$required ? props.theme.redNSP : props.theme.black1000};
    text-align: center;

    small {
      display: block;
      color: ${(props) =>
        props.$required ? props.theme.redNSP : props.theme.black700};
      font-size: 0.875rem;
      font-weight: 400;
    }
  }

  ${Button} {
    width: 100%;
    justify-content: center;
    font-weight: 600;
    border-radius: ${(props) => props.theme.borderRadius};
  }
`;

const ContactFormLink = styled.p`
  color: ${(props) => props.theme.black700};
  text-align: center;
`;
const StyledWrapper = styled.main`
  text-align: center;
  padding: 1.5rem 1.5rem 5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    text-align: left;
    padding: 2rem 0;
    max-width: 680px;
    margin: 0 auto;
  }

  & > header {
    & > * {
      margin: 0;
      padding: 0;
      line-height: 1.5;
      font-weight: 400;
    }

    h3 {
      font-size: 1rem;
      font-weight: 600;
    }

    h2 {
      padding: 0.25rem 0;
      font-weight: 700;
      font-size: 1.25rem;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        font-size: 1.625rem;
      }
    }

    h5 {
      font-size: 0.875rem;
      color: ${(props) => props.theme.black700};
    }
  }

  & > section {
    display: grid;
    grid-template-columns: 100%;
    grid-gap: 1.5rem;
  }
`;

const EventRequiredDocuments = (props) => {
  const {
    event,
    subtypes,
    status,
    dismissedDocumentTypes = [],
    requiredDocumentTypes = [],
    documents = [],
    limitDate,
    onChangeSubtype,
    onSaveDocument,
    onDismissDocument,
    isLoading,
    errors,
  } = props;

  const [isCollapsed, setIsCollapsed] = useState(true);
  const [selectedType, setSelectedType] = useState(null);

  const [required, unrequired] = useMemo(() => {
    const documentTypes = Object.keys(EVENT_DOCUMENT_TYPES);
    const sentDocumentTypes = documents.map((doc) => doc.type);

    const required = Array.isArray(requiredDocumentTypes)
      ? requiredDocumentTypes.filter(
          (type) =>
            !dismissedDocumentTypes.includes(type) &&
            !sentDocumentTypes.includes(type)
        )
      : [];

    if (required.length === documentTypes.length) {
      return [required, []];
    }

    if (required.length === 0) {
      return [required, documentTypes];
    }

    return [required, documentTypes.filter((type) => !required.includes(type))];
  }, [requiredDocumentTypes, dismissedDocumentTypes, documents]);

  const expand = () => setIsCollapsed(false);

  const selectType = (type) => {
    setSelectedType(type);
  };

  const unselectType = () => {
    setSelectedType(null);
  };

  return (
    <StyledWrapper>
      <IndexLinkAnchor route="events">
        <FeatherIcon name="arrow-left" /> &nbsp; Liste des événements
      </IndexLinkAnchor>
      <header>
        <h3>Documents de l'événement public</h3>
        <h2>{event.name}</h2>
        <h5>
          {dateFromISOString(event.endTime).toLocaleString({
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </h5>
      </header>
      <Spacer size="1.5rem" />
      <section>
        {requiredDocumentTypes.length === 0 && <NoRequiredDocumentCard />}
        <ProjectStatusCard status={status} />
        <SentDocumentsCard documents={documents} />
        <EventSubtypePicker
          value={event.subtype}
          options={subtypes}
          onChange={onChangeSubtype}
        />
      </section>
      <Spacer size="2rem" />
      {required.length > 0 && (
        <StyledDocumentList $required>
          <h4>
            {required.length}{" "}
            {required.length > 1
              ? "informations requises"
              : "information requise"}
            <small>À compléter avant le {displayShortDate(limitDate)}</small>
          </h4>
          <Spacer size="1.5rem" />
          {required.map((type, i) => (
            <RequiredDocumentCard
              key={type}
              type={type}
              onUpload={selectType}
              onDismiss={onDismissDocument}
              style={{ marginTop: i && "1rem" }}
            />
          ))}
        </StyledDocumentList>
      )}
      {unrequired.length > 0 && (
        <StyledDocumentList>
          <h4>
            Ajouter d’autres documents
            <small>Ajoutez-en autant que nécessaire</small>
          </h4>
          <Spacer size="1.5rem" />
          {isCollapsed ? (
            <Button $block onClick={expand}>
              Voir tout{" "}
              <FeatherIcon width="1.5rem" height="1.5rem" name="chevron-down" />
            </Button>
          ) : (
            unrequired.map((type, i) => (
              <RequiredDocumentCard
                key={type}
                type={type}
                onUpload={selectType}
                style={{ marginTop: i && "1rem" }}
              />
            ))
          )}
        </StyledDocumentList>
      )}
      <Spacer size="2rem" />
      <ContactFormLink>
        Besoin d'aide&nbsp;? Vous pouvez nous contacter via{" "}
        <a href="https://infos.actionpopulaire.fr/contact/">
          le formulaire en ligne
        </a>
      </ContactFormLink>
      <RequiredDocumentModal
        type={selectedType}
        shouldShow={!!selectedType}
        isLoading={isLoading}
        onClose={unselectType}
        onSubmit={onSaveDocument}
        errors={errors}
      />
    </StyledWrapper>
  );
};

EventRequiredDocuments.propTypes = {
  projectId: PropTypes.number,
  event: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    endTime: PropTypes.string.isRequired,
    subtype: PropTypes.shape({
      id: PropTypes.number.isRequired,
      description: PropTypes.string.isRequired,
    }),
  }),
  status: PropTypes.string,
  dismissedDocumentTypes: PropTypes.arrayOf(PropTypes.string),
  requiredDocumentTypes: PropTypes.arrayOf(PropTypes.string),
  documents: PropTypes.arrayOf(PropTypes.object),
  limitDate: PropTypes.string,

  subtypes: PropTypes.arrayOf(PropTypes.object),

  onSaveDocument: PropTypes.func.isRequired,
  onDismissDocument: PropTypes.func.isRequired,
  onChangeSubtype: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  errors: PropTypes.object,
};

export default EventRequiredDocuments;
