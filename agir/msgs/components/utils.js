import { displayShortDate } from "@agir/lib/utils/time";

export const getMessageSubject = (message) => {
  if (message?.subject) {
    return message.subject;
  }
  if (message?.created) {
    return `Message du ${displayShortDate(message.created)}`;
  }
  return "Message";
};
