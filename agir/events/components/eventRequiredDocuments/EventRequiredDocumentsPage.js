import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import useSWR from "swr";

import EventRequiredDocuments from "./EventRequiredDocuments";

import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import {
  addEventProjectDocument,
  getEventEndpoint,
  updateEvent,
  updateEventProject,
} from "@agir/events/common/api";
import { useEventFormOptions } from "@agir/events/common/hooks";
import Redirect from "@agir/front/app/Redirect";
import { routeConfig } from "@agir/front/app/routes.config";

const EventRequiredDocumentsUploadPage = (props) => {
  const { eventPk, embedded } = props;
  const { data, mutate, error } = useSWR(
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
      await updateEvent(eventPk, { subtype });
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

  if (error?.response?.status === 403 || error?.response?.status === 404) {
    return <Redirect to={routeConfig.eventDetails.getLink({ eventPk })} />;
  }

  return (
    <PageFadeIn ready={!!data}>
      {data && (
        <EventRequiredDocuments
          projectId={projectId}
          event={event}
          status={status}
          dismissedDocumentTypes={dismissedDocumentTypes}
          requiredDocumentTypes={requiredDocumentTypes}
          documents={documents}
          limitDate={limitDate}
          subtypes={subtype}
          isLoading={isLoading}
          errors={errors}
          onSaveDocument={saveDocument}
          onDismissDocument={dismissDocumentType}
          onChangeSubtype={changeSubtype}
          embedded={embedded}
        />
      )}
    </PageFadeIn>
  );
};

EventRequiredDocumentsUploadPage.propTypes = {
  eventPk: PropTypes.string.isRequired,
  embedded: PropTypes.bool,
};

const EventRequiredDocumentsPage = (props) => {
  const { eventPk, embedded } = props;

  const { data: event, error } = useSWR(
    getEventEndpoint("getDetailAdvanced", { eventPk })
  );

  if (error?.response?.status === 403 || error?.response?.status === 404) {
    return <Redirect to={routeConfig.eventDetails.getLink({ eventPk })} />;
  }

  return (
    <PageFadeIn ready={!!event}>
      {event && !embedded ? <OpenGraphTags title={event.name} /> : null}
      {event?.hasProject ? (
        <EventRequiredDocumentsUploadPage {...props} />
      ) : (
        <EventRequiredDocuments
          downloadOnly
          event={event}
          embedded={embedded}
        />
      )}
    </PageFadeIn>
  );
};

EventRequiredDocumentsPage.propTypes = {
  eventPk: PropTypes.string.isRequired,
  embedded: PropTypes.bool,
};

export default EventRequiredDocumentsPage;
