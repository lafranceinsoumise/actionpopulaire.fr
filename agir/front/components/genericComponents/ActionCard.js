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
                <Button
                  onClick={onConfirm}
                  small
                  color="secondary"
                  disabled={disabled}
                >
                  {confirmLabel}
                </Button>
              ) : typeof onConfirm === "string" ? (
                <Button
                  small
                  color="secondary"
                  as="a"
                  href={onConfirm}
                  disabled={disabled}
                >
                  {confirmLabel}
                </Button>
              ) : null}
              {typeof onDismiss === "function" ? (
                <Button onClick={onDismiss} small disabled={disabled}>
                  {dismissLabel}
                </Button>
              ) : typeof onDismiss === "string" ? (
                <Button small as="a" href={onDismiss} disabled={disabled}>
                  {dismissLabel}
                </Button>
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
  iconName: PropTypes.string.isRequired,
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
