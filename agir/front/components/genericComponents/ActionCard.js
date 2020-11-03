import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { Container, Row, Column } from "@agir/front/genericComponents/grid";
import Card from "@agir/front/genericComponents/Card";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const StyledButton = styled(Button)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
`;

const ActionCard = (props) => {
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
            {typeof onConfirm === "function" ? (
              <StyledButton onClick={onConfirm} small color="primary">
                {confirmLabel}
              </StyledButton>
            ) : typeof onConfirm === "string" ? (
              <StyledButton small color="primary" as="a" href={onConfirm}>
                {confirmLabel}
              </StyledButton>
            ) : null}
            &ensp;
            {typeof onDismiss === "function" ? (
              <StyledButton onClick={onDismiss} small color="dismiss">
                {dismissLabel}
              </StyledButton>
            ) : typeof onDismiss === "string" ? (
              <StyledButton small color="dismiss" as="a" href={onDismiss}>
                {dismissLabel}
              </StyledButton>
            ) : null}
          </Column>
        </Row>
      </Container>
    </Card>
  );
};

ActionCard.propTypes = {
  name: PropTypes.string.isRequired,
  text: PropTypes.node.isRequired,
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
  onConfirm: PropTypes.oneOfType([PropTypes.string, PropTypes.func]).isRequired,
  dismissLabel: PropTypes.string,
  onDismiss: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
};
ActionCard.defaultProps = {
  dismissLabel: "Cacher",
};

export default ActionCard;
