import React from "react";
import PropTypes from "prop-types";
import EventHeader from "./EventHeader";
import EventLocation from "./EventLocation";
import FacebookLink from "./FacebookLink";
import Description from "./Description";
import { DateTime } from "luxon";

const EventPage = (props) => {
  props = {
    ...props,
    startTime: DateTime.fromISO(props.startTime).setLocale("fr"),
    endTime: DateTime.fromISO(props.endTime).setLocale("fr"),
  };

  return (
    <div>
      <EventHeader {...props} />
      <EventLocation {...props} />
      <Description {...props} />
      <FacebookLink {...props} />
    </div>
  );
};
EventPage.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.string),
  illustration: PropTypes.string,
  description: PropTypes.string,
  startTime: PropTypes.string,
  endTime: PropTypes.string,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
  }),
  routes: PropTypes.shape({
    page: PropTypes.string,
    map: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    manage: PropTypes.string,
    calendarExport: PropTypes.string,
    googleExport: PropTypes.string,
    outlookExport: PropTypes.string,
    facebook: PropTypes.string,
  }),
};

export default EventPage;
