import PropTypes from "prop-types";
import React from "react";

import Card from "./GroupPageCard";
import Button from "@agir/front/genericComponents/Button";

const GroupFacts = (props) => {
  const { url } = props;

  return url ? (
    <Card title="Financez les actions du groupe">
      <p>
        Pour que ce groupe puisse financer ses frais de fonctionnement et
        s’équiper en matériel, vous pouvez contribuer financièrement.
      </p>
      <p>Chaque euro compte.</p>
      <Button href={url} link color="secondary" style={{ marginTop: "0.5rem" }}>
        Faire un don
      </Button>
    </Card>
  ) : null;
};

GroupFacts.propTypes = {
  url: PropTypes.string,
};
export default GroupFacts;
