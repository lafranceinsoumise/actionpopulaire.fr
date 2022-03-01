import { displayShortDate } from "@agir/lib/utils/time";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

export const getMessageSubject = (message) => {
  if (message?.subject) {
    return message.subject;
  }
  if (message?.created) {
    return `Message du ${displayShortDate(message.created)}`;
  }
  return "Message";
};
