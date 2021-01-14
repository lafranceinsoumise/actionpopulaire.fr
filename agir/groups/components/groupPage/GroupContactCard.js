import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Avatar from "@agir/front/genericComponents/Avatar";
import Card from "./GroupPageCard";

const StyledReferentSection = styled.section`
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
  const { referents, contact } = props;

  if (!referents && !contact) {
    return null;
  }

  return (
    <Card>
      {Array.isArray(referents) && referents.length > 0 ? (
        <StyledReferentSection>
          <p>
            {referents.map((referent, i) => (
              <React.Fragment key={i}>
                {i > 0 ? " " : null}
                <Avatar {...referent} name={referent.fullName} />
              </React.Fragment>
            ))}
          </p>
          <p>
            {referents.map((referent, i) => (
              <React.Fragment key={i}>
                {i > 0 ? " & " : null}
                <strong>{referent.fullName}</strong>
              </React.Fragment>
            ))}
          </p>
          <p>Animateur·ices de l’équipe</p>
        </StyledReferentSection>
      ) : null}
      {contact ? (
        <StyledContactSection>
          {contact.name && <strong>Contacter {contact.name}&nbsp;:</strong>}
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
  referents: PropTypes.arrayOf(
    PropTypes.shape({
      fullName: PropTypes.string.isRequired,
      avatar: PropTypes.string,
    })
  ),
  contact: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
  }),
};
export default GroupContactCard;
