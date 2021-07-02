import PropTypes from "prop-types";
import React from "react";

import { routeConfig } from "@agir/front/app/routes.config";

import Card from "@agir/front/genericComponents/Card";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";

import Link from "@agir/front/app/Link";

const EventInfoCard = ({ groups, participantCount, subtype }) => (
  <Card>
    <IconList>
      {groups.length > 0 && (
        <IconListItem name="users">
          Organisé par{" "}
          {groups.map(({ name, id }, key) => (
            <React.Fragment key={key}>
              {id ? (
                <Link to={routeConfig.groupDetails.getLink({ groupPk: id })}>
                  {name}
                </Link>
              ) : (
                name
              )}
              {key < groups.length - 2
                ? ", "
                : key === groups.length - 2
                ? " et "
                : ""}
            </React.Fragment>
          ))}
        </IconListItem>
      )}
      {subtype?.label && (
        <IconListItem name="folder">
          {subtype.label[0].toUpperCase()}
          {subtype.label.slice(1)}
        </IconListItem>
      )}
      {participantCount > 1 && (
        <IconListItem name="user-check">
          {participantCount} participant⋅es
        </IconListItem>
      )}
    </IconList>
  </Card>
);

EventInfoCard.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({ name: PropTypes.string, url: PropTypes.string })
  ),
  subtype: PropTypes.shape({
    label: PropTypes.string,
  }),
  participantCount: PropTypes.number,
};

export default EventInfoCard;
