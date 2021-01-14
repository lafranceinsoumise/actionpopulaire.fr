import PropTypes from "prop-types";
import React from "react";

import Card from "./GroupPageCard";
import Collapsible from "@agir/front/genericComponents/Collapsible";

const GroupDescription = (props) => {
  const { description } = props;

  if (!description || !String(description).trim()) {
    return null;
  }

  return (
    <Card title="Présentation">
      <Collapsible
        dangerouslySetInnerHTML={{ __html: description.trim() }}
        expanderLabel="Lire la suite"
        maxHeight={92}
        fadingOverflow
      />
    </Card>
  );
};

GroupDescription.propTypes = {
  description: PropTypes.string,
};
export default GroupDescription;
