import PropTypes from "prop-types";
import React from "react";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";
import Card from "@agir/front/genericComponents/Card";

const EventInfoCard = ({ groups, participantCount }) => (
  <Card>
    <IconList>
      {groups.length > 0 && (
        <IconListItem name="users">
          Organisé par{" "}
          {groups.map(({ name, url }, key) => (
            <>
              <a key={key} href={url}>
                {name}
              </a>
              {key < groups.length - 2
                ? ", "
                : key === groups.length - 2
                ? " et "
                : ""}
            </>
          ))}
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
  participantCount: PropTypes.number.isRequired,
};

export default EventInfoCard;
