import PropTypes from "prop-types";
import React from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Collapsible from "@agir/front/genericComponents/Collapsible.js";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

import GroupIconLfi from "./images/group-icon__lfi.svg";
import GroupIconNsp from "./images/group-icon__nsp.svg";

const Label = styled.span`
  font-size: 13px;
  display: inline-block;
  padding: 6px 10px;
  border: 1px solid #dfdfdf;
  margin-right: 8px;
  margin-bottom: 4px;
  line-height: 16px;
  height: 28px;
  border-radius: 20px;
  ${({ main }) =>
    main
      ? `
    background: #EEEEEE;
    border: 0;
    `
      : ""}
`;

const DiscountCodesSection = styled.section`
  margin: 1.5rem 0 0;

  & > * {
    color: ${style.black700};
    margin: 0.5rem 0;
  }

  ul {
    padding: 0;
  }

  li {
    list-style: none;
  }

  li span {
    font-weight: 400;
  }
`;

let GroupButton = ({
  as = "a",
  to,
  href,
  children,
  color = "default",
  icon,
}) => (
  <Column width={["33%", "content"]} collapse={500}>
    <Button as={as} to={to} href={href} color={color} icon={icon} small>
      {children}
    </Button>
  </Column>
);
GroupButton.propTypes = {
  as: PropTypes.string,
  to: PropTypes.string,
  href: PropTypes.string,
  children: PropTypes.node,
  color: PropTypes.string,
  icon: PropTypes.string,
};

const GroupCard = ({
  id,
  name,
  description,
  eventCount,
  membersCount,
  isMember,
  isManager,
  typeLabel,
  labels,
  routes,
  discountCodes,
  displayGroupLogo,
  displayType,
  displayDescription,
  displayMembership,
  isEmbedded = false,
  is2022 = false,
}) => {
  const history = useHistory();
  const handleClick = React.useCallback(
    (e) => {
      if (["A", "BUTTON"].includes(e.target.tagName.toUpperCase())) {
        return;
      }
      id &&
        routeConfig.groupDetails &&
        history.push(routeConfig.groupDetails.getLink({ groupPk: id }));
    },
    [history, id]
  );
  const Svg = React.useMemo(() => (is2022 ? GroupIconNsp : GroupIconLfi), [
    is2022,
  ]);
  return (
    <Card onClick={isEmbedded ? undefined : handleClick}>
      <Row gutter={6}>
        {displayGroupLogo && (
          <Column collapse={0}>
            <Link to={routeConfig.groupDetails.getLink({ groupPk: id })}>
              <img src={Svg} alt="Groupe" />
            </Link>
          </Column>
        )}
        <Column collapse={0} grow>
          <h3 style={{ marginTop: 2, marginBottom: 2 }}>
            <Link
              style={{
                color: "inherit",
                textDecoration: "none",
              }}
              to={routeConfig.groupDetails.getLink({ groupPk: id })}
            >
              {name}
            </Link>
          </h3>
          <small style={{ color: style.black500 }}>
            {eventCount} événement{eventCount > 1 ? "s" : ""} &bull;{" "}
            {membersCount} membre{membersCount > 1 ? "s" : ""}
          </small>
        </Column>
      </Row>

      {displayType && typeLabel && (
        <div style={{ marginTop: "24px" }}>
          <Label main>{typeLabel}</Label>
          {labels &&
            labels.map((label, index) => <Label key={index}>{label}</Label>)}
        </div>
      )}

      {displayDescription && description && (
        <div style={{ margin: "24px 0" }}>
          <Collapsible
            maxHeight={100}
            expanderLabel="Lire la suite"
            dangerouslySetInnerHTML={{ __html: description }}
            fadingOverflow
          />
        </div>
      )}

      {discountCodes && discountCodes.length > 0 && (
        <DiscountCodesSection>
          <h5>Codes matériels :</h5>
          <ul>
            {discountCodes.map(({ code, expirationDate }) => (
              <li key={code}>
                {code}{" "}
                <span>
                  (expire {expirationDate.toRelativeCalendar({ unit: "days" })})
                </span>
              </li>
            ))}
          </ul>
        </DiscountCodesSection>
      )}
      <Row gutter={6} style={{ marginTop: "1.5rem" }}>
        {!isMember ? (
          <GroupButton
            color="primary"
            as="Link"
            to={routeConfig.groupDetails.getLink({ groupPk: id })}
          >
            Rejoindre
            <Hide as="span" under={800}>
              &nbsp;le groupe
            </Hide>
          </GroupButton>
        ) : null}
        <GroupButton
          as="Link"
          to={routeConfig.groupDetails.getLink({ groupPk: id })}
        >
          Voir le groupe
        </GroupButton>
        {routes.fund && (
          <GroupButton href={routes.fund} icon="fast-forward">
            Financer
          </GroupButton>
        )}
        {isManager && routes.manage && (
          <GroupButton href={routes.manage} icon="settings">
            Gestion
          </GroupButton>
        )}
      </Row>
      {displayMembership && isMember && (
        <div style={{ marginTop: "1em" }}>
          <FeatherIcon small inline name="check" /> Vous êtes membre du groupe
        </div>
      )}
    </Card>
  );
};

GroupCard.propTypes = {
  name: PropTypes.string.isRequired,
  description: PropTypes.string,
  eventCount: PropTypes.number.isRequired,
  membersCount: PropTypes.number.isRequired,
  isMember: PropTypes.bool,
  isManager: PropTypes.bool,
  typeLabel: PropTypes.string,
  labels: PropTypes.arrayOf(PropTypes.string),
  routes: PropTypes.shape({
    page: PropTypes.string.isRequired,
    fund: PropTypes.string,
    manage: PropTypes.string,
  }),
  displayGroupLogo: PropTypes.bool,
  displayType: PropTypes.bool,
  displayDescription: PropTypes.bool,
  displayMembership: PropTypes.bool,
  ...DiscountCodesSection.propTypes,
  isEmbedded: PropTypes.bool,
  is2022: PropTypes.bool,
};

GroupCard.defaultProps = {
  displayGroupLogo: true,
  displayType: true,
  displayDescription: true,
  displayMembership: true,
  isManager: false,
  is2022: false,
};

export default GroupCard;
