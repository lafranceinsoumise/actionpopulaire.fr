import PropTypes from "prop-types";
import React, { useState, useMemo } from "react";
import { useTransition } from "@react-spring/web";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";
import { SubtypeOptions } from "@agir/events/common/SubtypePanel";
import {
  DefaultOption,
  StyledDefaultOptions,
} from "@agir/events/createEventPage/EventForm/SubtypeField";

import { EVENT_TYPES } from "@agir/events/common/utils";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const EventSubtypeField = (props) => {
  const { name, value, options, onChange, disabled } = props;

  const subtypeOptions = useMemo(() => {
    if (!Array.isArray(options) || options.length === 0) {
      return [];
    }
    const categories = {};
    options.forEach((subtype) => {
      const category =
        subtype.type && EVENT_TYPES[subtype.type] ? subtype.type : "O";
      categories[category] = categories[category] || {
        ...EVENT_TYPES[category],
      };
      categories[category].subtypes = categories[category].subtypes || [];
      categories[category].subtypes.push(subtype);
    });

    return Object.values(categories).filter((category) =>
      Array.isArray(category.subtypes)
    );
  }, [options]);

  const selectedSubtype = useMemo(
    () =>
      typeof value === "number"
        ? options.find((option) => option.id === value)
        : value,
    [value, options]
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

      {value && (
        <div>
          <StyledDefaultOptions style={{ display: "inline-flex" }}>
            <DefaultOption
              option={selectedSubtype}
              onClick={openMenu}
              disabled={disabled}
              selected
            />
          </StyledDefaultOptions>
          <Button
            type="button"
            color="link"
            onClick={openMenu}
            style={{ marginLeft: "0.5rem" }}
            disabled={disabled}
          >
            Changer
          </Button>
        </div>
      )}

      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <BackButton onClick={closeMenu} />
              <StyledTitle>Choisir le type de l'événement</StyledTitle>
              <Spacer size="1rem" />
              <SubtypeOptions
                disabled={disabled}
                options={subtypeOptions}
                onClick={handleChangeSubtype}
                selected={selectedSubtype}
              />
            </PanelWrapper>
          )
      )}
    </>
  );
};

EventSubtypeField.propTypes = {
  name: PropTypes.string,
  value: PropTypes.object,
  options: PropTypes.arrayOf(PropTypes.object),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
};

export default EventSubtypeField;
