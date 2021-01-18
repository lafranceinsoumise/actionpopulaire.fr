import PropTypes from "prop-types";
import React from "react";

import Card from "./GroupPageCard";
import Collapsible from "@agir/front/genericComponents/Collapsible";

const GroupDescription = (props) => {
  const { description, maxHeight = 92, routes } = props;

  if (!description || !String(description).trim()) {
    return null;
  }

  return (
    <Card title="Présentation" editUrl={routes && routes.edit}>
      <Collapsible
        dangerouslySetInnerHTML={{ __html: description.trim() }}
        expanderLabel="Lire la suite"
        maxHeight={maxHeight}
        fadingOverflow
      />
    </Card>
  );
};

GroupDescription.propTypes = {
  description: PropTypes.string,
  maxHeight: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  routes: PropTypes.object,
};
export default GroupDescription;
