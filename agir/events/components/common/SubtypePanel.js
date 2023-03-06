import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import Button from "@agir/front/genericComponents/Button";
import Panel from "@agir/front/genericComponents/Panel";

import { EVENT_TYPES } from "@agir/events/common/utils";
import Spacer from "@agir/front/genericComponents/Spacer";
import FaIcon from "@agir/front/genericComponents/FaIcon";

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

  & > ${Button} {
    visibility: ${({ $selected }) => ($selected ? "hidden" : "visible")};
    margin-left: auto;
  }

  & > :first-child {
    color: ${style.primary500};
    display: inline-block;
    font-size: 1rem;
    line-height: 1;
    height: 1rem;
    width: 1rem;
    padding-top: 0.25rem;
    text-align: center;
  }

  & > strong {
    font-weight: 400;
    padding: 0 0 0 1rem;
  }
`;

const StyledOptions = styled.div`
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

const SubtypeOption = (props) => {
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
      <FaIcon
        icon={option?.iconName || "calendar"}
        style={{ color: option.color }}
      />
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
    color: PropTypes.string,
    description: PropTypes.string,
  }),
  onClick: PropTypes.func,
  selected: PropTypes.bool,
};

export const SubtypeOptions = ({ options, onClick, selected }) => {
  return (
    <StyledOptions>
      {options.map((category) => (
        <ul key={category.label}>
          <strong title={category.description}>{category.label}</strong>
          {category.subtypes.map((subtype) => (
            <SubtypeOption
              key={category.label + subtype.id}
              onClick={onClick}
              option={subtype}
              selected={!!selected && selected.id === subtype.id}
            />
          ))}
        </ul>
      ))}
    </StyledOptions>
  );
};

SubtypeOptions.propTypes = {
  onClick: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  selected: PropTypes.object,
};

const SubtypeField = (props) => {
  const { shouldShow, onChange, onClose, value, options, lastUsedIds } = props;
  const panelPosition = useResponsiveMemo("right", "left");

  const optionCategories = useMemo(() => {
    const categories = Object.entries(EVENT_TYPES).reduce(
      (result, [type, config]) => ({
        ...result,
        [type]: {
          ...config,
          subtypes: [],
        },
      }),
      {}
    );
    const subtypes = Array.isArray(options) ? options : [];

    subtypes.forEach((subtype) => {
      const category =
        subtype.type && categories[subtype.type] ? subtype.type : "O";
      categories[category].subtypes = categories[category].subtypes || [];
      categories[category].subtypes.push(subtype);
    });

    return Object.values(categories).filter(
      (category) =>
        Array.isArray(category.subtypes) && category.subtypes.length > 0
    );
  }, [options]);

  const lastUsedOptions = useMemo(() => {
    const subtypes = Array.isArray(options) ? options : [];

    if (!Array.isArray(lastUsedIds)) {
      return null;
    }

    const lastUsed = lastUsedIds
      .map((id) => subtypes.find((subtype) => subtype.id === id))
      .filter(Boolean);

    if (lastUsed.length === 0) {
      return null;
    }

    return [
      {
        label: "Derniers types utilisés",
        description:
          "Les types choisis pour les derniers événements que vous avez créé",
        subtypes: lastUsed,
      },
    ];
  }, [options, lastUsedIds]);

  return (
    <Panel
      position={panelPosition}
      shouldShow={shouldShow}
      onClose={onClose}
      onBack={onClose}
      title="Type de l'événement"
      noScroll
    >
      {lastUsedOptions && (
        <>
          <SubtypeOptions
            options={lastUsedOptions}
            onClick={onChange}
            selected={value}
          />
          <Spacer size="1rem" />
        </>
      )}
      <SubtypeOptions
        options={optionCategories}
        onClick={onChange}
        selected={value}
      />
    </Panel>
  );
};
SubtypeField.propTypes = {
  onClose: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object,
  options: PropTypes.arrayOf(PropTypes.object),
  lastUsedIds: PropTypes.arrayOf(PropTypes.number),
  shouldShow: PropTypes.bool,
};
export default SubtypeField;
