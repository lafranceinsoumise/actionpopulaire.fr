import PropTypes from "prop-types";
import Card from "./Card";
import React from "react";
import { IconList, IconListItem } from "./FeatherIcon";

const Contact = ({ name, phone, email }) => (
  <Card>
    <p>
      <b>Contact</b>
    </p>
    <IconList>
      <IconListItem name="user">{name}</IconListItem>
      <IconListItem name="phone">{phone}</IconListItem>
      <IconListItem name="mail">{email}</IconListItem>
    </IconList>
  </Card>
);

Contact.propTypes = {
  name: PropTypes.string,
  phone: PropTypes.string,
  email: PropTypes.string,
};

export default Contact;
