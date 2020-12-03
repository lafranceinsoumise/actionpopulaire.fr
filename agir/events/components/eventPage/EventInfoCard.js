import PropTypes from "prop-types";
import React from "react";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";
import Card from "@agir/front/genericComponents/Card";

const EventInfoCard = ({ groups, participantCount, is2022 }) => (
  <Card>
    <IconList>
      {groups.length > 0 && (
        <IconListItem name="users">
          Organisé par{" "}
          {groups.map(({ name, routes }, key) => (
            <React.Fragment key={key}>
              {routes && routes.page ? <a href={routes.page}>{name}</a> : name}
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
        {is2022 ? "Évènement Nous sommes pour !" : "Évènement France insoumise"}
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
  participantCount: PropTypes.number.isRequired,
  is2022: PropTypes.bool,
};

export default EventInfoCard;
