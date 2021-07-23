import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import Button from "@agir/front/genericComponents/Button";
import Panel from "@agir/front/genericComponents/Panel";

import { EVENT_TYPES } from "@agir/events/common/utils";

const StyledOption = styled.li`
  display: flex;
  flex-flow: row nowrap;
  min-height: 2.75rem;
  align-items: flex-start;
  font-size: 1rem;
  line-height: 1.5;
  color: ${({ $selected }) => ($selected ? style.primary500 : style.black1000)};
  font-weight: ${({ $selected }) => ($selected ? 600 : 400)};
  cursor: ${({ $selected }) => ($selected ? "default" : "pointer")};

  & + & {
    padding-top: 0.5rem;
  }

  & > button {
    display: ${({ $selected }) => ($selected ? "none" : "inline")};
    margin-left: auto;
  }

  & > span {
    color: ${style.primary500};
    display: inline-block;
    font-size: 1rem;
    line-height: 1;
    height: 1rem;
    width: 1rem;
    padding-top: 0.25rem;
  }

  & > strong {
    font-weight: 400;
    padding: 0 0.5rem;
  }
`;

export const StyledOptions = styled.div`
  display: flex;
  flex-flow: column nowrap;
  padding-top: 0.5rem;

  ul {
    padding: 0;
    list-style: none;

    & > strong {
      display: block;
      height: 2.75rem;
      font-weight: 600;
      font-size: 1rem;
      line-height: 1.5;
      display: flex;
      align-items: center;
    }
  }
`;

export const SubtypeOption = (props) => {
  const { option, onClick, selected } = props;

  const handleClick = useCallback(() => {
    onClick(option);
  }, [option, onClick]);

  return (
    <StyledOption
      $selected={selected}
      title={option.description}
      onClick={handleClick}
    >
      <span className={`fa fa-${option.iconName || "calendar"}`} />
      <strong>
        {option.description && (
          <>
            {option.description[0].toUpperCase()}
            {option.description.slice(1)}
          </>
        )}
      </strong>
      <Button type="button" color="choose" onClick={handleClick} small>
        Choisir
      </Button>
    </StyledOption>
  );
};

SubtypeOption.propTypes = {
  option: PropTypes.shape({
    id: PropTypes.number,
    label: PropTypes.string,
    iconName: PropTypes.string,
    color: PropTypes.String,
    description: PropTypes.string,
  }),
  onClick: PropTypes.func,
  selected: PropTypes.bool,
};

const SubtypeField = (props) => {
  const { shouldShow, onChange, onClose, value } = props;

  const panelPosition = useResponsiveMemo("right", "left");

  const subtypes = useMemo(
    () => (Array.isArray(props.options) ? props.options : []),
    [props.options]
  );

  const options = useMemo(() => {
    const categories = {};
    subtypes.forEach((subtype) => {
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
  }, [subtypes]);

  return (
    <Panel
      position={panelPosition}
      shouldShow={shouldShow}
      onClose={onClose}
      onBack={onClose}
      title="Type de l'événement"
      noScroll
    >
      <StyledOptions>
        {options.map((category) => (
          <ul key={category.label}>
            <strong title={category.description}>{category.label}</strong>
            {category.subtypes.map((subtype) => (
              <SubtypeOption
                key={subtype.id}
                onClick={onChange}
                option={subtype}
                selected={!!value && value.id === subtype.id}
              />
            ))}
          </ul>
        ))}
      </StyledOptions>
    </Panel>
  );
};
SubtypeField.propTypes = {
  onClose: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  shouldShow: PropTypes.bool,
};
export default SubtypeField;
