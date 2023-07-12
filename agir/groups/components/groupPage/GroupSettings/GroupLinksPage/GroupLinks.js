import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import LinkIcon from "@agir/front/genericComponents/LinkIcon";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const GroupLink = styled.button`
  display: flex;
  align-items: center;
  width: 100%;
  padding: 1rem 0;
  cursor: pointer;
  background-color: transparent;
  outline: none;
  border: none;
  border-collapse: collapse;
  border-top: 1px solid ${(props) => props.theme.black100};
  border-bottom: 1px solid ${(props) => props.theme.black100};
  margin-top: -1px;

  ${RawFeatherIcon} {
    flex: 0 0 auto;

    &:first-child {
      color: ${(props) => props.theme.primary500};
    }
  }

  strong {
    font-weight: 400;
    flex: 1 1 auto;
    padding: 0 0.5rem;
    text-align: left;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
`;

const GroupLinks = (props) => {
  const { links, onEdit } = props;

  const createNewLink = () => onEdit({});

  if (!Array.isArray(links) || links.length === 0) {
    return (
      <>
        <div>
          Vous n’avez pas encore de lien !
          <Spacer size="0.5rem" />
          Ajoutez vos réseaux sociaux et sites web pour permettre à tout le
          monde de les retrouver facilement
        </div>
        <Spacer size="1rem" />
        <Button color="secondary" onClick={createNewLink}>
          Ajouter un lien
        </Button>
      </>
    );
  }

  return (
    <>
      {links.map((link) => (
        <GroupLink key={link.id} onClick={() => onEdit(link)}>
          <LinkIcon url={link.url} />
          <strong>{link.label}</strong>
          <RawFeatherIcon name="edit-2" width="1rem" height="1rem" />
        </GroupLink>
      ))}
      <Button icon="plus" color="link" onClick={createNewLink}>
        Ajouter un lien
      </Button>
    </>
  );
};
GroupLinks.propTypes = {
  onEdit: PropTypes.func.isRequired,
  links: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number,
      label: PropTypes.string,
      url: PropTypes.string,
    }),
  ),
};
export default GroupLinks;
