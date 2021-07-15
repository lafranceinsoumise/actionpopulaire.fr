import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import useSWR from "swr";

import EventRequiredDocument from "./EventRequiredDocuments";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import {
  getEventEndpoint,
  updateEvent,
  updateEventProject,
  addEventProjectDocument,
} from "@agir/events/common/api";
import { useEventFormOptions } from "@agir/events/common/hooks";

const EventRequiredDocumentsPage = (props) => {
  const { eventPk } = props;
  const { data, mutate } = useSWR(
    getEventEndpoint("eventProject", { eventPk })
  );
  const { subtype } = useEventFormOptions();

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState(null);

  const {
    projectId,
    event,
    status,
    dismissedDocumentTypes,
    requiredDocumentTypes,
    documents,
    limitDate,
  } = data || {};

  const changeSubtype = useCallback(
    async (subtype) => {
      setIsLoading(true);
      await updateEvent(eventPk, { subtype: subtype.id });
      setIsLoading(false);
      mutate();
    },
    [eventPk, mutate]
  );

  const saveDocument = useCallback(
    async (doc) => {
      setIsLoading(true);
      setErrors(null);
      const result = await addEventProjectDocument(eventPk, doc);
      if (result.errors) {
        setErrors(result.errors);
      } else {
        mutate();
      }
      setIsLoading(false);
    },
    [eventPk, mutate]
  );

  const dismissDocumentType = useCallback(
    async (documentType) => {
      if (dismissedDocumentTypes.includes(documentType)) {
        mutate();
        return;
      }
      setIsLoading(true);
      setErrors(null);
      const result = await updateEventProject(eventPk, {
        dismissedDocumentTypes: [...dismissedDocumentTypes, documentType],
      });
      if (result.errors) {
        setErrors(result.errors);
      } else {
        mutate();
      }
      setIsLoading(false);
    },
    [eventPk, dismissedDocumentTypes, mutate]
  );

  const requiredDocumentTypesLeft = useMemo(() => {
    if (!documents) {
      return;
    }
    const sentDocumentTypes = documents.map((doc) => doc.type);
    return requiredDocumentTypes.filter(
      (type) =>
        !dismissedDocumentTypes.includes(type) &&
        !sentDocumentTypes.includes(type)
    );
  }, [dismissedDocumentTypes, requiredDocumentTypes, documents]);

  return (
    <PageFadeIn ready={!!data}>
      {data && (
        <EventRequiredDocument
          projectId={projectId}
          event={event}
          status={status}
          requiredDocumentTypes={requiredDocumentTypesLeft}
          documents={documents}
          limitDate={limitDate}
          subtypes={subtype}
          isLoading={isLoading}
          errors={errors}
          onSaveDocument={saveDocument}
          onDismissDocument={dismissDocumentType}
          onChangeSubtype={changeSubtype}
        />
      )}
    </PageFadeIn>
  );
};

EventRequiredDocumentsPage.propTypes = {
  eventPk: PropTypes.string.isRequired,
  route: PropTypes.shape({
    backLink: PropTypes.object,
  }),
};
export default EventRequiredDocumentsPage;
