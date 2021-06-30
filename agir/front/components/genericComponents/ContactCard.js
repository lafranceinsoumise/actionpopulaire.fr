import PropTypes from "prop-types";
import Card from "./Card";
import React from "react";
import { IconList, IconListItem } from "./FeatherIcon";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const StyledCard = styled(Card)`
  margin-bottom: 24px;
  box-shadow: ${style.cardShadow};
  border-radius: ${style.borderRadius};
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const ContactCard = ({ name, phone, email }) => (
  <StyledCard>
    <p>
      <b>Contact</b>
    </p>
    <IconList>
      {name && <IconListItem name="user">{name}</IconListItem>}
      {phone && <IconListItem name="phone">{phone}</IconListItem>}
      {email && <IconListItem name="mail">{email}</IconListItem>}
    </IconList>
  </StyledCard>
);

ContactCard.propTypes = {
  name: PropTypes.string,
  phone: PropTypes.string,
  email: PropTypes.string,
};

export default ContactCard;
