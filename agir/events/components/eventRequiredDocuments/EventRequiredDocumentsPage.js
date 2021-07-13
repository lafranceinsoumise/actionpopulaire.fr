import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import useSWR from "swr";

import EventRequiredDocument from "./EventRequiredDocuments";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import { getEventEndpoint, updateEvent } from "@agir/events/common/api";
import { useEventFormOptions } from "@agir/events/common/hooks";

const EventRequiredDocumentsPage = (props) => {
  const { eventPk } = props;
  const { data, mutate } = useSWR(
    getEventEndpoint("eventProject", { eventPk })
  );
  const { subtype } = useEventFormOptions();

  const [isLoading, setIsLoading] = useState(false);

  const {
    projectId,
    event,
    status,
    dismissedDocumentTypes,
    requiredDocumentTypes,
    documents,
    limitDate,
  } = data || {};

  const handleChangeSubtype = useCallback(
    async (subtype) => {
      setIsLoading(true);
      await updateEvent(eventPk, { subtype: subtype.id });
      setIsLoading(false);
      mutate();
    },
    [eventPk, mutate]
  );

  return (
    <PageFadeIn ready={!!data}>
      {data && (
        <EventRequiredDocument
          projectId={projectId}
          event={event}
          status={status}
          requiredDocumentTypes={requiredDocumentTypes.filter(
            (type) => !dismissedDocumentTypes.includes(type)
          )}
          documents={documents}
          limitDate={limitDate}
          subtypes={subtype}
          isLoading={isLoading}
          onSaveDocument={console.log}
          onDismissDocument={console.log}
          onChangeSubtype={handleChangeSubtype}
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
