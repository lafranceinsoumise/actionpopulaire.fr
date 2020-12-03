import PropTypes from "prop-types";
import Card from "./Card";
import React from "react";
import { IconList, IconListItem } from "./FeatherIcon";

const ContactCard = ({ name, phone, email }) => (
  <Card>
    <p>
      <b>Contact</b>
    </p>
    <IconList>
      {name && <IconListItem name="user">{name}</IconListItem>}
      {phone && <IconListItem name="phone">{phone}</IconListItem>}
      {email && <IconListItem name="mail">{email}</IconListItem>}
    </IconList>
  </Card>
);

ContactCard.propTypes = {
  name: PropTypes.string,
  phone: PropTypes.string,
  email: PropTypes.string,
};

export default ContactCard;
