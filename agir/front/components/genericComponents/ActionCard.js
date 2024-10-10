import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { dateFromISOString, displayHumanDate } from "@agir/lib/utils/time";

import Card from "@agir/front/genericComponents/Card";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const CardContainer = styled.div`
  display: flex;
  gap: 10px;
`

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

  & > * {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    text-align: left;
    transition: all 250ms ease-in-out;

    &[disabled] {
      cursor: default;
    }

    &.inactive {
      font-size: 0;
      color: transparent;
      padding: 0;
      border-width: 0;
      margin-left: -0.5rem;
    }
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
    dismissed,
    timestamp,
  } = props;

  const date = useMemo(
    () =>
      timestamp &&
      displayHumanDate(dateFromISOString(timestamp))
        .split("")
        .map((ch, i) => (i ? ch : ch.toUpperCase()))
        .join(""),
    [timestamp],
  );

  return (
    <Card type={dismissed ? "alert_dismissed" : "alert"}>
      <CardContainer>
          <div>
            {dismissed ? (
              <FeatherIcon name="check-circle" color="success500" />
            ) : (
              <FeatherIcon name={iconName} />
            )}
          </div>
          <div>
            <StyledText>
              {text}
              <br />
              <em>{date ? date : null}</em>
            </StyledText>
            <StyledFooter>
              {(typeof onConfirm === "string" ||
                typeof onConfirm === "function") && (
                <Button
                  small
                  link={typeof onConfirm === "string"}
                  onClick={
                    typeof onConfirm === "function" ? onConfirm : undefined
                  }
                  href={typeof onConfirm === "string" ? onConfirm : undefined}
                  disabled={disabled}
                  className={dismissed ? "inactive" : ""}
                  color="primary"
                >
                  {confirmLabel}
                </Button>
              )}
              {(typeof onDismiss === "string" ||
                typeof onDismiss === "function") && (
                <Button
                  small
                  link={typeof onDismiss === "string"}
                  onClick={
                    typeof onDismiss === "function" ? onDismiss : undefined
                  }
                  href={typeof onDismiss === "string" ? onDismiss : undefined}
                  disabled={disabled}
                  color="default"
                >
                  {dismissed ? "Marquer comme non traité" : dismissLabel}
                </Button>
              )}
            </StyledFooter>
          </div>
      </CardContainer>
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
  dismissed: PropTypes.bool,
  timestamp: PropTypes.string,
};
ActionCard.defaultProps = {
  dismissLabel: "Cacher",
  disabled: false,
  dismissed: false,
};

export default ActionCard;
