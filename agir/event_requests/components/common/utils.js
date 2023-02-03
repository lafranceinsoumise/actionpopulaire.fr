export const parseEventSpeakerRequests = (speaker) => {
  if (!speaker) {
    return {};
  }

  const eventRequests = speaker.eventRequests.reduce(
    (obj, request) => ({
      ...obj,
      [request.id]: request,
    }),
    {}
  );
  const answerable = {};
  const unanswerable = {};

  speaker.eventSpeakerRequests.forEach((eventSpeakerRequest) => {
    let target = eventSpeakerRequest.isAnswerable ? answerable : unanswerable;
    target = target[eventSpeakerRequest.eventRequest] =
      target[eventSpeakerRequest.eventRequest] || [];
    target.push(eventSpeakerRequest);
  });

  return {
    answerable: Object.entries(answerable).reduce(
      (arr, [eventRequestId, eventSpeakerRequests]) => {
        arr.push({
          ...eventRequests[eventRequestId],
          eventSpeakerRequests,
        });
        return arr;
      },
      []
    ),
    unanswerable: Object.entries(unanswerable).reduce(
      (arr, [eventRequestId, eventSpeakerRequests]) => {
        arr.push({
          ...eventRequests[eventRequestId],
          eventSpeakerRequests,
        });
        return arr;
      },
      []
    ),
  };
};
