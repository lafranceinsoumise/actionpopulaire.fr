import PropTypes from "prop-types";
import React, { Fragment, useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import {
  EVENT_TYPES,
  PRIVATE_EVENT_SUBTYPE_INFO,
  getEventSubtypeInfo,
} from "@agir/events/common/utils";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import FaIcon from "@agir/front/genericComponents/FaIcon";
import TextField from "@agir/front/formComponents/TextField";
import Accordion from "@agir/front/genericComponents/Accordion";
import Button from "@agir/front/genericComponents/Button";
import Panel from "@agir/front/genericComponents/Panel";
import { slugify } from "@agir/lib/utils/url";

const StyledIcon = styled(FaIcon)``;
const StyledOption = styled.li`
  width: 100%;
  display: flex;
  flex-flow: row nowrap;
  min-height: 2rem;
  align-items: center;
  line-height: 1.5;
  color: ${({ $selected }) => ($selected ? style.primary500 : style.black1000)};
  cursor: ${({ $selected }) => ($selected ? "default" : "pointer")};
  font-size: 1rem;
  gap: 0.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
  }

  & + & {
    padding-top: 0.5rem;
  }

  & > ${Button} {
    flex: 0 0 auto;
    visibility: ${({ $selected }) => ($selected ? "hidden" : "visible")};
    margin-left: auto;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.75rem;
    }
  }

  & > ${StyledIcon} {
    flex: 0 0 auto;
    height: 2rem;
    width: 2rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 1.5rem;
      width: 1.5rem;
    }
  }

  & > strong {
    font-weight: 400;
    padding: 0;
    font-weight: ${({ $selected }) => ($selected ? 500 : 400)};
  }
`;

const StyledOptions = styled.ul`
  padding: 1rem 0.5rem;
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
`;

const StyledEmptyMessage = styled.p`
  color: ${(props) => props.theme.black700};
  padding: 1rem 0.5rem;
`;

const StyledSubtypePicker = styled.div`
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;
`;

const SubtypeOption = (props) => {
  const { option, onClick, selected } = props;

  const handleClick = useCallback(() => {
    onClick(option);
  }, [option, onClick]);

  const title = getEventSubtypeInfo(option);

  return (
    <StyledOption
      $selected={selected}
      title={option.description}
      onClick={handleClick}
    >
      <StyledIcon icon={option.iconName} style={{ color: option.color }} />
      <abbr title={title || undefined}>
        {option.description && (
          <>
            {option.description[0].toUpperCase()}
            {option.description.slice(1)}
          </>
        )}
      </abbr>
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
    isPrivate: PropTypes.bool,
    forGroupType: PropTypes.string,
    forGroups: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string,
        name: PropTypes.string,
      })
    ),
  }),
  onClick: PropTypes.func,
  selected: PropTypes.bool,
};

export const SubtypeOptions = ({ options, onClick, selected }) => {
  return options.map((category) => (
    <Accordion
      key={category.label}
      name={category.label}
      counter={category.subtypes.length}
      small
      isDefaultOpen
    >
      <StyledOptions title={category.description}>
        {category.subtypes.map((subtype) => (
          <SubtypeOption
            key={category.label + subtype.id}
            onClick={onClick}
            option={subtype}
            selected={!!selected && selected.id === subtype.id}
          />
        ))}
      </StyledOptions>
    </Accordion>
  ));
};

SubtypeOptions.propTypes = {
  onClick: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  selected: PropTypes.object,
};

export const SubtypePicker = (props) => {
  const { value, onChange, options, lastUsedIds, disabled } = props;
  const [searchTerm, setSearchTerm] = useState("");
  const term = useMemo(() => slugify(searchTerm), [searchTerm]);

  const subtypes = useMemo(() => {
    const allSubtypes = Array.isArray(options) ? options : [];
    if (!term) {
      return allSubtypes;
    }
    return allSubtypes.filter((subtype) =>
      slugify(subtype.description).includes(term)
    );
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

    [...subtypes].reverse().forEach((subtype) => {
      const category =
        subtype.type && categories[subtype.type] ? subtype.type : "O";
      categories[category].subtypes = categories[category].subtypes || [];
      if (/^(tout )?autre/i.test(subtype.description)) {
        categories[category].subtypes.push(subtype);
      } else {
        categories[category].subtypes.unshift(subtype);
      }
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
    <StyledSubtypePicker>
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
      <div>
        {subtypes.length > 0 ? (
          <>
            {!term && lastUsedOptions && (
              <SubtypeOptions
                options={lastUsedOptions}
                onClick={onChange}
                selected={value}
                disabled={disabled}
              />
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
      </div>
    </StyledSubtypePicker>
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
