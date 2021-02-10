import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import Card from "./GroupPageCard";

const StyledManagerSection = styled.section`
  margin-bottom: 1.5rem;

  &:empty {
    display: none;
    margin: 0;
  }

  ${Avatar} {
    width: 4rem;
    height: 4rem;
  }

  && p {
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;

    &:nth-child(2) {
      font-size: 1.125rem;

      @media (max-width: ${style.collapse}px) {
        font-size: 1rem;
      }
    }

    && strong {
      font-weight: 600;
    }
  }
`;
const StyledContactSection = styled.p`
  font-size: 14px;
  line-height: 1.5;
  display: flex;
  flex-flow: column nowrap;

  && strong {
    font-weight: 600;
  }

  && a {
    font-weight: 500;
    text-decoration: none;
    color: ${style.primary500};
    cursor: pointer;
  }
`;

const GroupContactCard = (props) => {
  const { managers, contact, routes } = props;

  if (!managers && !contact) {
    return null;
  }

  return (
    <Card>
      {Array.isArray(managers) && managers.length > 0 ? (
        <StyledManagerSection>
          <p>
            {managers.map((manager, i) => (
              <React.Fragment key={i}>
                {i > 0 ? " " : null}
                <Avatar {...manager} name={manager.displayName} />
              </React.Fragment>
            ))}
          </p>
          <p>
            {managers.map((manager, i) => (
              <React.Fragment key={i}>
                {i > 0 ? " & " : null}
                <strong>{manager.displayName}</strong>
              </React.Fragment>
            ))}
          </p>
          <p>Animateur·ices de l’équipe</p>
        </StyledManagerSection>
      ) : null}
      {contact ? (
        <StyledContactSection>
          {contact.name && (
            <strong>
              Contact&ensp;
              {routes && routes.edit && (
                <a href={routes.edit}>
                  <RawFeatherIcon
                    name="edit-2"
                    color={style.black1000}
                    width="0.875rem"
                    height="0.875rem"
                  />
                </a>
              )}
            </strong>
          )}
          {contact.name && <span>{contact.name}</span>}
          {contact.email && (
            <a href={`mailto:${contact.email}`}>{contact.email}</a>
          )}
          {contact.phone && <span>{contact.phone}</span>}
        </StyledContactSection>
      ) : null}
    </Card>
  );
};

GroupContactCard.propTypes = {
  managers: PropTypes.arrayOf(
    PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      avatar: PropTypes.string,
    })
  ),
  contact: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
  }),
  routes: PropTypes.object,
};
export default GroupContactCard;
