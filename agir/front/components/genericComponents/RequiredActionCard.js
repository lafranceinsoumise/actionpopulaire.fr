import PropTypes from "prop-types";
import React from "react";

import { Container, Row, Column } from "@agir/front/genericComponents/grid";
import Card from "@agir/front/genericComponents/Card";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const RequiredActionCard = (props) => {
  const {
    text,
    iconName,
    confirmLabel,
    onConfirm,
    dismissLabel,
    onDismiss,
  } = props;
  return (
    <Card type="primary">
      <Container>
        <Row>
          <Column width={40} collapse={0} style={{ padding: 0 }}>
            <FeatherIcon name={iconName} />
          </Column>
          <Column grow collapse={0}>
            <p style={{ fontWeight: 600, fontSize: 14, marginBottom: 16 }}>
              {text}
            </p>
            <Button onClick={onConfirm} small color="primary">
              {confirmLabel}
            </Button>
            &ensp;
            {typeof onDismiss === "function" && (
              <Button onClick={onDismiss} small color="dismiss">
                {dismissLabel}
              </Button>
            )}
          </Column>
        </Row>
      </Container>
    </Card>
  );
};

RequiredActionCard.propTypes = {
  name: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  iconName: PropTypes.oneOf([
    "alert-circle",
    "calendar",
    "file-text",
    "info",
    "mail",
    "user-plus",
    "x-circle",
  ]).isRequired,
  confirmLabel: PropTypes.string.isRequired,
  onConfirm: PropTypes.func.isRequired,
  dismissLabel: PropTypes.string,
  onDismiss: PropTypes.func,
};
RequiredActionCard.defaultProps = {
  dismissLabel: "Cacher",
};

export default RequiredActionCard;
