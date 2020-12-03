import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { Container, Row, Column } from "@agir/front/genericComponents/grid";
import Card from "@agir/front/genericComponents/Card";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const StyledText = styled.p`
  && {
    font-weight: 400;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 16px;
  }
`;
const StyledFooter = styled.footer`
  display: flex;
  flex-flow: row nowrap;
`;
const StyledButton = styled(Button)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-align: left;

  &[disabled] {
    cursor: default;
  }

  & + & {
    margin-left: 0.5rem;
  }
`;

const ActionCard = (props) => {
  const {
    text,
    iconName,
    confirmLabel,
    onConfirm,
    dismissLabel,
    onDismiss,
    disabled,
  } = props;
  return (
    <Card type="alert">
      <Container style={{ width: "auto" }}>
        <Row justify="flex-start">
          <Column width="auto" collapse={0} style={{ padding: 0 }}>
            <FeatherIcon name={iconName} />
          </Column>
          <Column grow collapse={0}>
            <StyledText>{text}</StyledText>
            <StyledFooter>
              {typeof onConfirm === "function" ? (
                <StyledButton
                  onClick={onConfirm}
                  small
                  color="secondary"
                  disabled={disabled}
                >
                  {confirmLabel}
                </StyledButton>
              ) : typeof onConfirm === "string" ? (
                <StyledButton
                  small
                  color="secondary"
                  as="a"
                  href={onConfirm}
                  disabled={disabled}
                >
                  {confirmLabel}
                </StyledButton>
              ) : null}
              {typeof onDismiss === "function" ? (
                <StyledButton onClick={onDismiss} small disabled={disabled}>
                  {dismissLabel}
                </StyledButton>
              ) : typeof onDismiss === "string" ? (
                <StyledButton small as="a" href={onDismiss} disabled={disabled}>
                  {dismissLabel}
                </StyledButton>
              ) : null}
            </StyledFooter>
          </Column>
        </Row>
      </Container>
    </Card>
  );
};

ActionCard.propTypes = {
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
  disabled: PropTypes.bool,
};
ActionCard.defaultProps = {
  dismissLabel: "Cacher",
  disabled: false,
};

export default ActionCard;
