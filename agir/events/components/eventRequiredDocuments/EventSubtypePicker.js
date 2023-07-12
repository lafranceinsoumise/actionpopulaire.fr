import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";

import SubtypePanel from "@agir/events/common/SubtypePanel";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledCurrentValue = styled.button`
  &,
  &:hover,
  &:focus {
    border-radius: ${(props) => props.theme.borderRadius};
    box-shadow: ${(props) => props.theme.cardShadow};
    height: 56px;
    width: 100%;
    padding: 0 1rem;
    margin: 0;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: transparent;
    border: none;
    outline: none;
    text-align: left;
    min-width: 1px;

    strong {
      padding-right: 1rem;
      flex: 1 1 auto;
      overflow-x: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-weight: 600;
      font-size: 1rem;
      color: ${(props) => props.theme.primary500};

      &::first-letter {
        text-transform: uppercase;
      }
    }
  }
`;

const EventSubtypePicker = (props) => {
  const { onChange, value, disabled } = props;

  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const openPanel = () => {
    setIsPanelOpen(true);
  };

  const closePanel = () => {
    setIsPanelOpen(false);
  };

  const handleChange = (subtype) => {
    onChange(subtype);
    closePanel();
  };

  const subtypes = useMemo(
    () => (Array.isArray(props.options) ? props.options : []),
    [props.options],
  );

  return (
    <>
      <StyledCurrentValue onClick={openPanel} disabled={disabled}>
        <strong>{value.description}</strong>
        <RawFeatherIcon name="edit-3" />
      </StyledCurrentValue>
      <SubtypePanel
        onClose={closePanel}
        onChange={handleChange}
        value={value}
        options={subtypes}
        shouldShow={isPanelOpen}
      />
    </>
  );
};
EventSubtypePicker.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  disabled: PropTypes.bool,
};
export default EventSubtypePicker;
