import { useTransition } from "@react-spring/web";
import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";

import { SubtypePicker } from "@agir/events/common/SubtypePanel";
import {
  DefaultOption,
  StyledDefaultOptions,
} from "@agir/events/createEventPage/EventForm/SubtypeField";
import Button from "@agir/front/genericComponents/Button";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import Spacer from "@agir/front/genericComponents/Spacer";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const EventSubtypeField = (props) => {
  const { name, value, options, lastUsedIds, onChange, disabled } = props;

  const selectedSubtype = useMemo(
    () =>
      typeof value === "number"
        ? options.find((option) => option.id === value)
        : value,
    [value, options],
  );

  const [isOpen, setIsOpen] = useState(false);

  const openMenu = () => setIsOpen(true);
  const closeMenu = () => setIsOpen(false);

  const handleChangeSubtype = (subtype) => {
    onChange(name, subtype);
    closeMenu();
  };

  const transition = useTransition(isOpen, slideInTransition);

  return (
    <>
      <div>
        <label>Type de l'événement</label>
      </div>

      <div>
        <StyledDefaultOptions style={{ display: "inline-flex" }}>
          {selectedSubtype && (
            <DefaultOption
              option={selectedSubtype}
              onClick={openMenu}
              disabled={disabled}
              selected
            />
          )}
        </StyledDefaultOptions>
        <Button
          type="button"
          color="link"
          onClick={openMenu}
          style={{ marginLeft: "0.5rem" }}
          disabled={disabled}
        >
          {!!selectedSubtype ? "Changer" : "Choisir"}
        </Button>
      </div>

      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <BackButton onClick={closeMenu} />
              <StyledTitle>Choisir le type de l'événement</StyledTitle>
              <Spacer size="1rem" />
              <SubtypePicker
                value={selectedSubtype}
                onChange={handleChangeSubtype}
                options={options}
                lastUsedIds={lastUsedIds}
                disabled={disabled}
              />
            </PanelWrapper>
          ),
      )}
    </>
  );
};

EventSubtypeField.propTypes = {
  name: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.object]),
  options: PropTypes.arrayOf(PropTypes.object),
  lastUsedIds: PropTypes.arrayOf(PropTypes.number),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
};

export default EventSubtypeField;
