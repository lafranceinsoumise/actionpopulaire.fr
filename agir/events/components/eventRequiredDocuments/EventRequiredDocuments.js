import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";

import { dateFromISOString, displayShortDate } from "@agir/lib/utils/time";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import EventSubtypePicker from "./EventSubtypePicker";
import ProjectStatusCard from "./ProjectStatusCard";
import RequiredDocumentCard from "./RequiredDocumentCard";
import RequiredDocumentModal from "./RequiredDocumentModal";
import SentDocumentsCard from "./SentDocumentsCard";

import BackLink from "@agir/front/app/Navigation/BackLink";
import { EVENT_DOCUMENT_TYPES } from "./config";

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

    small {
      display: block;
      color: ${(props) =>
        props.$required ? props.theme.redNSP : props.theme.black700};
      font-size: 0.875rem;
      font-weight: 400;
    }
  }
`;

const HelpLink = styled.div`
  color: ${(props) => props.theme.black700};

  & > div {
    display: flex;
    gap: 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex-direction: column;
    }
  }
`;

const StyledWrapper = styled.main`
  padding: ${({ $embedded }) => ($embedded ? "1rem 0" : "1.5rem 1.5rem 5rem")};

  @media (min-width: ${(props) => props.theme.collapse}px) {
    text-align: left;
    padding: ${({ $embedded }) => ($embedded ? "1rem 0" : "2rem 0")};
    max-width: 680px;
    margin: 0 auto;
  }

  & > section:empty + ${Spacer} {
    display: none;
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

  ${StyledDocumentList} {
    text-align: ${({ $embedded }) => ($embedded ? "left" : "center")};
  }

  ${HelpLink} > div {
    justify-content: ${({ $embedded }) =>
      $embedded ? "flex-start" : "center"};
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
    embedded,
    downloadOnly,
  } = props;

  const [isCollapsed, setIsCollapsed] = useState(!embedded && !downloadOnly);
  const [selectedType, setSelectedType] = useState(null);

  const [required, unrequired] = useMemo(() => {
    const documentTypes = Object.keys(EVENT_DOCUMENT_TYPES);
    const sentDocumentTypes = documents.map((doc) => doc.type);

    if (downloadOnly) {
      return [[], documentTypes];
    }

    const required = Array.isArray(requiredDocumentTypes)
      ? requiredDocumentTypes.filter(
          (type) =>
            !dismissedDocumentTypes.includes(type) &&
            !sentDocumentTypes.includes(type),
        )
      : [];

    if (required.length === documentTypes.length) {
      return [required, []];
    }

    if (required.length === 0) {
      return [required, documentTypes];
    }

    return [required, documentTypes.filter((type) => !required.includes(type))];
  }, [downloadOnly, requiredDocumentTypes, dismissedDocumentTypes, documents]);

  const expand = () => setIsCollapsed(false);

  const selectType = (type) => {
    setSelectedType(type);
  };

  const unselectType = () => {
    setSelectedType(null);
  };

  return (
    <StyledWrapper $embedded={embedded}>
      {!embedded && <BackLink style={{ marginLeft: 0 }} />}
      {!embedded && (
        <>
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
        </>
      )}
      <section>
        {typeof status !== "undefined" && (
          <ProjectStatusCard
            status={status}
            hasRequiredDocuments={requiredDocumentTypes.length > 0}
            hasMissingDocuments={required.length > 0}
            hasDismissedAllDocuments={
              requiredDocumentTypes.length <= dismissedDocumentTypes.length
            }
          />
        )}
        {Array.isArray(documents) && (
          <SentDocumentsCard documents={documents} />
        )}
        {!embedded && onChangeSubtype && event.subtype.isVisible && (
          <EventSubtypePicker
            value={event.subtype}
            options={subtypes}
            onChange={onChangeSubtype}
          />
        )}
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
          <Spacer size="1rem" />
          <p style={{ textAlign: "inherit", lineHeight: 1.6 }}>
            Si votre événement n’a pas eu recours a un élément demandé, vous
            pouvez cliquer sur le bouton “non applicable”.
          </p>
          <Spacer size="1.5rem" />
          {required.map((type, i) => (
            <RequiredDocumentCard
              key={type}
              type={type}
              onUpload={selectType}
              onDismiss={onDismissDocument}
              style={{ marginTop: i && "1rem" }}
              embedded={embedded}
            />
          ))}
        </StyledDocumentList>
      )}
      {unrequired.length > 0 && (
        <StyledDocumentList>
          {required.length > 0 && (
            <>
              <h4>
                Ajouter d’autres documents
                <small>Ajoutez-en autant que nécessaire</small>
              </h4>
              <Spacer size="1.5rem" />
            </>
          )}
          {isCollapsed ? (
            <Button
              style={{ width: "100%" }}
              onClick={expand}
              icon="chevron-down"
              rightIcon
            >
              Voir tout
            </Button>
          ) : (
            unrequired.map((type, i) => (
              <RequiredDocumentCard
                key={type}
                type={type}
                onUpload={selectType}
                style={{ marginTop: i && "1rem" }}
                embedded={embedded}
                downloadOnly={downloadOnly}
              />
            ))
          )}
        </StyledDocumentList>
      )}
      <Spacer size="2rem" />
      <HelpLink>
        Besoin d'aide&nbsp;?
        <Spacer size="1rem" />
        <div>
          <Button link rel="noopener noreferrer" target="_blank" route="help">
            Accèder au centre d'aide
          </Button>
        </div>
      </HelpLink>
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
      isVisible: PropTypes.bool,
    }),
  }),
  status: PropTypes.string,
  dismissedDocumentTypes: PropTypes.arrayOf(PropTypes.string),
  requiredDocumentTypes: PropTypes.arrayOf(PropTypes.string),
  documents: PropTypes.arrayOf(PropTypes.object),
  limitDate: PropTypes.string,
  subtypes: PropTypes.arrayOf(PropTypes.object),
  onSaveDocument: PropTypes.func,
  onDismissDocument: PropTypes.func,
  onChangeSubtype: PropTypes.func,
  isLoading: PropTypes.bool,
  errors: PropTypes.object,
  embedded: PropTypes.bool,
  downloadOnly: PropTypes.bool,
};

export default EventRequiredDocuments;
