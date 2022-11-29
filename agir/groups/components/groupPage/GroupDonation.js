import PropTypes from "prop-types";
import React from "react";

import Card from "./GroupPageCard";
import Button from "@agir/front/genericComponents/Button";

const GroupFacts = (props) => {
  const { id, isCertified } = props;

  if (!isCertified) {
    return null;
  }

  return (
    <Card title="Financez les actions du groupe">
      <p />
      <p>
        Pour que ce groupe puisse financer ses frais de fonctionnement et
        s’équiper en matériel, vous pouvez contribuer financièrement de manière
        ponctuelle ou mensuellement.
      </p>
      <p>Chaque euro compte.</p>
      <Button
        route="contributions"
        params={{ group: id }}
        link
        color="secondary"
        style={{ marginTop: "0.5rem" }}
      >
        Devenir financeur·euse
      </Button>
      <Button
        route="donations"
        params={{ group: id }}
        link
        color="secondary"
        style={{ marginTop: "0.5rem" }}
      >
        Faire un don ponctuel
      </Button>
    </Card>
  );
};

GroupFacts.propTypes = {
  id: PropTypes.string.isRequired,
  isCertified: PropTypes.bool,
};
export default GroupFacts;
