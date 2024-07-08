import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import { FaUsers } from "@agir/front/genericComponents/FaIcon";

const StyledOption = styled.button`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  width: 100%;
  border: none;
  margin: 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: left;
  color: ${(props) => props.theme.text1000};
  font-size: 1rem;
  padding: 0.5rem 0;

  &:last-child {
    margin-bottom: 0;
  }

  &:hover,
  &:focus {
    border: none;
    outline: none;
    background-color: ${(props) => props.theme.text50};
    text-decoration: none;
  }

  i {
    flex: 0 0 2rem;
    height: 2rem;
    background-color: ${(props) => props.theme.primary500};
    border-radius: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 0;
  }

  span {
    flex: 1 1 auto;
    line-height: 2;
    margin: 0 1rem;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

const StyledWarning = styled.p`
  display: flex;
  flex-flow: column nowrap;
  padding: 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 1.5rem 1rem;
  background-color: ${(props) => props.theme.text50};
  border-radius: ${(props) => props.theme.borderRadius};

  strong {
    font-weight: 600;
  }
`;

const StyledWrapper = styled.div`
  max-height: 360px;
  padding-top: 1.5rem;
  max-width: 100%;
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-height: 100%;
  }

  & > *:last-child {
    margin-bottom: 1.5rem;
  }

  h4,
  ${StyledOption} {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  h4 {
    color: ${(props) => props.theme.text1000};
    font-weight: 600;
    font-size: 1rem;
    line-height: 1.5;
    margin: 0 0 1rem;
  }
`;

const GroupStepOption = (props) => {
  const { group, onSelect } = props;

  return (
    <StyledOption onClick={() => onSelect(group)}>
      <i>
        <FaUsers color="background0" />
      </i>
      <span title={group.name}>{group.name}</span>
    </StyledOption>
  );
};
GroupStepOption.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string.isRequired,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
};

const GroupStep = (props) => {
  const { groups, onSelectGroup } = props;

  return (
    <StyledWrapper>
      <h4>À qui s'adresse ce message&nbsp;?</h4>
      <StyledWarning>
        <span>
          Les membres et abonné·es de votre groupe&nbsp;
          <strong>recevront un e-mail</strong> avec le contenu de votre message
          et <strong>pourront y répondre !</strong>
        </span>
      </StyledWarning>
      {groups.map((group) => (
        <GroupStepOption
          key={group.id}
          group={group}
          onSelect={onSelectGroup}
        />
      ))}
    </StyledWrapper>
  );
};
GroupStep.propTypes = {
  groups: PropTypes.arrayOf(GroupStepOption.propTypes.group).isRequired,
  onSelectGroup: PropTypes.func.isRequired,
};

export default GroupStep;
