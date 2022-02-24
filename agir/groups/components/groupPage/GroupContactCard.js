import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "./GroupPageCard";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledContactSection = styled.p`
  font-size: 14px;
  line-height: 1.5;
  display: flex;
  flex-flow: column nowrap;
  margin: 0;

  && strong {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }

  && a {
    font-weight: 500;
    text-decoration: none;
    color: ${style.primary500};
    cursor: pointer;
  }
`;

const GroupContactCard = (props) => {
  const { contact, editLinkTo } = props;

  if (!contact) {
    return null;
  }

  return (
    <Card>
      {contact ? (
        <StyledContactSection>
          {contact.name && (
            <strong>
              Moyens de contact&ensp;
              {editLinkTo && (
                <Link to={editLinkTo}>
                  <RawFeatherIcon
                    name="edit-2"
                    color={style.black1000}
                    width="1rem"
                    height="1rem"
                  />
                </Link>
              )}
            </strong>
          )}
          {contact.name && <span>{contact.name}</span>}
          {contact.email && (
            <a href={`mailto:${contact.email}`}>{contact.email}</a>
          )}
          {contact.phone && (
            <a href={`tel:${contact.phone}`} style={{ color: "inherit" }}>
              {contact.phone} {contact.hidePhone && " (caché)"}
            </a>
          )}
        </StyledContactSection>
      ) : null}
    </Card>
  );
};

GroupContactCard.propTypes = {
  contact: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
    hidePhone: PropTypes.bool,
  }),
  editLinkTo: PropTypes.string,
};

export default GroupContactCard;
