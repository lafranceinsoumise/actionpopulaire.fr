import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo } from "react";
import styled from "styled-components";

import CheckboxField from "@agir/front/formComponents/CheckboxField";

import { GROUP_SELECTION_MAX_LIMIT } from "./common";

const StyledLabel = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem 1.5rem;
  flex-flow: row nowrap;
  margin-bottom: 1rem;

  & > * {
    margin: 0;
  }
`;

const GroupSelectField = (props) => {
  const { groups, label, value, onChange, disabled, isLoading, displayZips } =
    props;

  const selectedGroups = useMemo(() => {
    if (!groups || !value.g) {
      return {};
    }

    return (Array.isArray(value.g) ? value.g : [value.g])
      .map((groupId) => groups.find(({ id }) => id === groupId))
      .filter(Boolean)
      .slice(0, GROUP_SELECTION_MAX_LIMIT + 1)
      .reduce(
        (obj, group) => ({
          ...obj,
          [group.id]: group,
        }),
        {},
      );
  }, [value.g, groups]);

  const handleChange = useCallback(
    (e) => {
      const { value, checked } = e.target;
      const currentValue = Object.keys(selectedGroups);

      onChange(
        "g",
        checked
          ? [...currentValue, value]
          : currentValue.filter((groupId) => groupId !== value),
      );
    },
    [selectedGroups, onChange],
  );

  const handleToggleSelectAll = useCallback(
    (e) => {
      const { checked } = e.target;
      if (checked) {
        onChange(
          "g",
          groups.map((group) => group.id),
        );
      } else {
        onChange("g", []);
      }
    },
    [groups, onChange],
  );

  useEffect(() => {
    if (isLoading) {
      return;
    }

    const currentValue = value.g
      ? Array.isArray(value.g)
        ? value.g
        : [value.g]
      : [];

    const extraGroups = currentValue.filter(
      (groupId, i) =>
        i >= GROUP_SELECTION_MAX_LIMIT || !selectedGroups[groupId],
    );

    if (extraGroups.length === 0) {
      return;
    }

    onChange(
      "g",
      currentValue.filter((groupId) => !extraGroups.includes(groupId)),
    );
  }, [isLoading, onChange, selectedGroups, value.g]);

  if (!Array.isArray(groups)) {
    return (
      <>
        <StyledLabel>{label}</StyledLabel>
        <p style={{ fontSize: "0.875rem", margin: 0 }}>
          <em>
            Sélectionnez un ou plusieurs codes postaux pour en afficher la liste
            des groupes d’action
          </em>
        </p>
      </>
    );
  }

  if (groups.length === 0) {
    return (
      <>
        <StyledLabel>{label}</StyledLabel>
        <p style={{ fontSize: "0.875rem", margin: 0 }}>
          <em>Aucun groupe n'a été trouvé</em>
        </p>
      </>
    );
  }

  return (
    <>
      {groups.length > 1 && groups.length <= GROUP_SELECTION_MAX_LIMIT && (
        <StyledLabel>
          {label}
          <CheckboxField
            toggle
            key="all"
            inputValue="all"
            value={Object.keys(selectedGroups).length === groups.length}
            onClick={handleToggleSelectAll}
            label={
              Object.keys(selectedGroups).length === groups.length
                ? "Tout désélectionner"
                : "Tout sélectionner"
            }
            disabled={disabled || isLoading}
            style={{ fontSize: "0.875rem" }}
          />
        </StyledLabel>
      )}
      <div>
        {groups.length > GROUP_SELECTION_MAX_LIMIT && (
          <p style={{ fontSize: "0.875rem", marginTop: "-0.5rem" }}>
            <em>
              Vous pouvez sélectionner jusqu'à {GROUP_SELECTION_MAX_LIMIT}{" "}
              groupes d'actions
            </em>
          </p>
        )}
        <div style={{ clear: "both" }} />
        {groups.map((group) => (
          <CheckboxField
            key={group.id}
            inputValue={group.id}
            value={!!selectedGroups[group.id]}
            onChange={handleChange}
            label={
              displayZips ? (
                <>
                  {group.name}&ensp;<small>{group.zip}</small>
                </>
              ) : (
                group.name
              )
            }
            disabled={
              disabled ||
              isLoading ||
              (!selectedGroups[group.id] &&
                Object.keys(selectedGroups).length >= GROUP_SELECTION_MAX_LIMIT)
            }
          />
        ))}
      </div>
    </>
  );
};

GroupSelectField.propTypes = {
  value: PropTypes.shape({
    g: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.string),
    ]),
    z: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.string),
    ]),
  }),
  onChange: PropTypes.func,
  groups: PropTypes.array,
  disabled: PropTypes.bool,
  isLoading: PropTypes.bool,
  displayZips: PropTypes.bool,
};

export default GroupSelectField;
