import PropTypes from "prop-types";
import React, { useMemo } from "react";

import Card from "@agir/front/genericComponents/Card";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const EventInfoCard = (props) => {
  const { groups, subtype, isManager, backLink } = props;
  return (
    <Card>
      <IconList>
        {subtype.description && (
          <IconListItem>
            <FaIcon
              style={{ color: subtype.color }}
              icon={subtype.iconName || "folder"}
            />
            <span>
              {subtype.description[0].toUpperCase()}
              {subtype.description.slice(1)}
            </span>
          </IconListItem>
        )}
        {groups.length > 1 && (
          <IconListItem name="users">
            Organisé par&nbsp;:
            {groups.map(({ name, id }, key) => (
              <div key={name + id}>
                {id ? (
                  <Link
                    route="groupDetails"
                    routeParams={{ groupPk: id }}
                    backLink={backLink}
                  >
                    {name}
                  </Link>
                ) : (
                  name
                )}
                {groups[key + 1] && ","}
              </div>
            ))}
          </IconListItem>
        )}
        {groups.length === 1 && (
          <IconListItem name="users">
            Organisé par{" "}
            {groups.map(({ name, id }) => (
              <React.Fragment key={name + id}>
                {id ? (
                  <Link
                    route="groupDetails"
                    routeParams={{ groupPk: id }}
                    backLink={backLink}
                  >
                    {name}
                  </Link>
                ) : (
                  name
                )}
              </React.Fragment>
            ))}
          </IconListItem>
        )}
      </IconList>
      <Spacer size="1rem" />
      {isManager && (
        <Button
          icon="plus"
          small
          link
          route="createEvent"
          params={{
            group: groups[0]?.id,
            subtype: subtype.label,
          }}
          color="primary"
          backLink={backLink}
        >
          Créer un événement similaire
        </Button>
      )}
    </Card>
  );
};

EventInfoCard.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      url: PropTypes.string,
    })
  ),
  subtype: PropTypes.shape({
    label: PropTypes.string,
    description: PropTypes.string,
    iconName: PropTypes.string,
    color: PropTypes.string,
  }),
  isManager: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default EventInfoCard;
