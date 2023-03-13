import PropTypes from "prop-types";
import React, { Fragment, useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { EVENT_TYPES } from "@agir/events/common/utils";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import TextField from "@agir/front/formComponents/TextField";
import Button from "@agir/front/genericComponents/Button";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import Panel from "@agir/front/genericComponents/Panel";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledOption = styled.li`
  display: flex;
  flex-flow: row nowrap;
  min-height: 2rem;
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

const StyledEmptyMessage = styled.p`
  color: ${(props) => props.theme.black700};
  padding: 1rem 0.5rem;
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

export const SubtypePicker = (props) => {
  const { value, onChange, options, lastUsedIds, disabled } = props;
  const [searchTerm, setSearchTerm] = useState("");
  const term = searchTerm.trim();

  const subtypes = useMemo(() => {
    const allSubtypes = Array.isArray(options) ? options : [];
    if (!term) {
      return allSubtypes;
    }
    const re = new RegExp(term, "i");
    return allSubtypes.filter((subtype) => re.test(subtype.description));
  }, [options, term]);

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
  }, [subtypes]);

  const lastUsedOptions = useMemo(() => {
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
  }, [subtypes, lastUsedIds]);

  return (
    <Fragment>
      {options.length > 0 && (
        <TextField
          id="ev-st-search"
          name="ev-st-search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Rechercher un type d'événement"
          aria-label="Rechercher un type d'événement"
          icon="search"
          label=""
          dark
        />
      )}
      {subtypes.length > 0 ? (
        <>
          {!term && lastUsedOptions && (
            <>
              <SubtypeOptions
                options={lastUsedOptions}
                onClick={onChange}
                selected={value}
                disabled={disabled}
              />
              <Spacer size="1rem" />
            </>
          )}
          <SubtypeOptions
            options={optionCategories}
            onClick={onChange}
            selected={value}
            disabled={disabled}
          />
        </>
      ) : (
        <StyledEmptyMessage>
          Aucun type d'événément n'a été trouvé
        </StyledEmptyMessage>
      )}
    </Fragment>
  );
};
SubtypePicker.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object,
  options: PropTypes.arrayOf(PropTypes.object),
  lastUsedIds: PropTypes.arrayOf(PropTypes.number),
  disabled: PropTypes.bool,
};

const SubtypePanel = (props) => {
  const { shouldShow, onClose, ...rest } = props;
  const panelPosition = useResponsiveMemo("right", "left");

  return (
    <Panel
      position={panelPosition}
      shouldShow={shouldShow}
      onClose={onClose}
      onBack={onClose}
      title="Type de l'événement"
      noScroll
    >
      <SubtypePicker {...rest} />
    </Panel>
  );
};

SubtypePanel.propTypes = {
  onClose: PropTypes.func.isRequired,
  shouldShow: PropTypes.bool,
};
export default SubtypePanel;
