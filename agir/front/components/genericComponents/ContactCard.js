import PropTypes from "prop-types";
import Card from "./Card";
import React from "react";
import { IconList, IconListItem } from "./FeatherIcon";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const StyledCard = styled(Card)`
  margin-bottom: 24px;
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const ContactCard = ({ name, phone, email }) =>
  phone || email ? (
    <StyledCard>
      <p>
        <b>Contact</b>
      </p>
      <IconList>
        {name && <IconListItem name="user">{name}</IconListItem>}
        {phone && (
          <IconListItem name="phone">
            <a
              href={`tel:${phone}`}
              style={{ color: "inherit", textDecoration: "none" }}
            >
              {phone}
            </a>
          </IconListItem>
        )}
        {email && <IconListItem name="mail">{email}</IconListItem>}
      </IconList>
    </StyledCard>
  ) : null;

ContactCard.propTypes = {
  name: PropTypes.string,
  phone: PropTypes.string,
  email: PropTypes.string,
};

export default ContactCard;
