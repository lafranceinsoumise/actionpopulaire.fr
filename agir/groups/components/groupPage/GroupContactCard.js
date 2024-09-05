import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Card from "./GroupPageCard";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ContactButton from "./GroupUserActions/ContactButton";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledContactSection = styled.p`
  font-size: 14px;
  line-height: 1.5;
  display: flex;
  flex-flow: column nowrap;
  align-items: start;
  margin: 0;
  gap: 0.5rem;

  && > strong {
    font-weight: 600;
    font-size: 1rem;
  }

  && > a {
    font-weight: 500;
    text-decoration: none;
    color: ${(props) => props.theme.primary500};
    cursor: pointer;
  }
`;

const GroupContactCard = (props) => {
  const { id, isMessagingEnabled, contact, editLinkTo } = props;

  if (!contact?.email && !contact?.phone && !isMessagingEnabled) {
    return null;
  }

  return (
    <Card>
      <StyledContactSection>
        <strong>
          Moyens de contact&ensp;
          {editLinkTo && (
            <Link to={editLinkTo}>
              <RawFeatherIcon
                name="edit-2"
                color="text1000"
                width="1rem"
                height="1rem"
              />
            </Link>
          )}
        </strong>
        {!!contact?.name && <span>{contact.name}</span>}
        {!!contact?.email && (
          <a href={`mailto:${contact.email}`}>{contact.email}</a>
        )}
        {!!contact?.phone && (
          <a href={`tel:${contact.phone}`} style={{ color: "inherit" }}>
            {contact.phone} {!!contact?.hidePhone && " (caché)"}
          </a>
        )}
        <Spacer size="0" />
        <ContactButton
          id={id}
          isMessagingEnabled={isMessagingEnabled}
          buttonTrigger
          contact={contact}
        />
      </StyledContactSection>
    </Card>
  );
};

GroupContactCard.propTypes = {
  id: PropTypes.string,
  isMessagingEnabled: PropTypes.bool,
  contact: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
    hidePhone: PropTypes.bool,
  }),
  editLinkTo: PropTypes.string,
};

export default GroupContactCard;
