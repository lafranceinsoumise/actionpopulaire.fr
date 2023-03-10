import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo } from "react";
import styled from "styled-components";

import { Link } from "@agir/donations/common/StyledComponents";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import SelectField from "@agir/front/formComponents/SelectField";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledWidget = styled.div`
  margin: 1rem 0;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: ${({ theme }) => theme.borderRadius};
  border: 1px solid ${({ theme }) => theme.black200};

  & > div {
    font-size: 0.875rem;
    flex: 1 1 auto;
    min-width: 1px;
  }

  & > ${RawFeatherIcon} {
    flex: 0 0 auto;
  }
`;

const StyledWidgetWithGroup = styled(StyledWidget)`
  border: none;
  background-color: ${({ theme }) => theme.default.primary100};

  & > div > span,
  & > ${RawFeatherIcon} {
    color: ${({ theme }) => theme.default.primary500};
  }

  & > div {
    display: flex;
    flex-flow: column nowrap;

    strong {
      display: block;
      font-weight: 500;
      font-size: 1rem;
    }
  }
`;

const SelectedGroupWidget = (props) => {
  const { group, groups, onChange } = props;

  const groupChoices = useMemo(
    () =>
      Array.isArray(groups)
        ? groups.map((g) => ({ ...g, value: g.id, label: g.name }))
        : [],
    [groups]
  );

  useEffect(() => {
    if (!group && groupChoices.length < 2) {
      onChange(groupChoices[0]);
    }
  }, [group, groupChoices, onChange]);

  if (group || groupChoices.length > 0) {
    return (
      <StyledWidgetWithGroup>
        <RawFeatherIcon name="arrow-right-circle" />
        <div>
          <span>Dons alloués au groupe d'action</span>
          {groupChoices.length > 1 && <Spacer size="0.25rem" />}
          {groupChoices.length > 1 ? (
            <SelectField
              label=""
              helpText=""
              name="group"
              placeholder="Selectionnez un groupe d'action certifié"
              value={groupChoices.find((g) => g.id === group?.id)}
              options={groupChoices}
              onChange={onChange}
              small
            />
          ) : (
            <strong>{group?.name}</strong>
          )}
        </div>
      </StyledWidgetWithGroup>
    );
  }

  return (
    <StyledWidget>
      <RawFeatherIcon name="info" />
      <div>
        Pour allouer une partie de votre don{" "}
        <strong>à un groupe d'action certifié</strong>, utilisez le bouton
        &laquo;&nbsp;financer&nbsp;&raquo; dans la page du groupe.{" "}
        <Link route="groupMap" params={{ subtype: "certifié" }}>
          Voir la carte des groupes d'action certifiés
        </Link>
        .
      </div>
    </StyledWidget>
  );
};

SelectedGroupWidget.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }),
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  onChange: PropTypes.func,
};

export default SelectedGroupWidget;
