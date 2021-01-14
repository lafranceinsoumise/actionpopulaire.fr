import PropTypes from "prop-types";
import React from "react";

import { routeConfig } from "@agir/front/app/routes.config";

import Card from "@agir/front/genericComponents/Card";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

const EventInfoCard = ({ groups, participantCount, is2022 }) => (
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
      <IconListItem name="flag">
        {is2022 ? "Événement Nous sommes pour !" : "Événement France insoumise"}
      </IconListItem>
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
  participantCount: PropTypes.number,
  is2022: PropTypes.bool,
};

export default EventInfoCard;
