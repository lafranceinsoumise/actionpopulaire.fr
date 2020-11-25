import React from "react";
import Card from "@agir/front/genericComponents/Card";
import PropTypes from "prop-types";

import Svg from "@agir/events/eventPage/group.svg";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Collapsible from "@agir/front/genericComponents/Collapsible.js";

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

const GroupButton = ({ href, children, color = "default", icon }) => (
  <Column width={["33%", "content"]} collapse={500}>
    <Button as="a" href={href} color={color} icon={icon} small>
      {children}
    </Button>
  </Column>
);

const GroupCard = ({
  name,
  description,
  eventCount,
  membersCount,
  isMember,
  typeLabel,
  labels,
  routes,
  discountCodes,
  displayGroupLogo,
  displayType,
  displayDescription,
  displayMembership,
}) => (
  <>
    <Card>
      <Row gutter={6}>
        {displayGroupLogo && (
          <Column collapse={0}>
            <img src={Svg} alt="Groupe" />
          </Column>
        )}
        <Column collapse={0} grow>
          <h3 style={{ marginTop: 2, marginBottom: 2 }}>{name}</h3>
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
        <GroupButton color="primary" href={routes.page}>
          {isMember ? (
            "Voir le groupe"
          ) : (
            <>
              Rejoindre
              <Hide as="span" under={800}>
                &nbsp;le groupe
              </Hide>
            </>
          )}
        </GroupButton>
        {routes.fund && (
          <GroupButton href={routes.fund} icon="fast-forward">
            Financer
          </GroupButton>
        )}
        {routes.manage && (
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
  </>
);

GroupCard.propTypes = {
  name: PropTypes.string.isRequired,
  description: PropTypes.string,
  eventCount: PropTypes.number.isRequired,
  membersCount: PropTypes.number.isRequired,
  isMember: PropTypes.bool,
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
};

GroupCard.defaultProps = {
  displayGroupLogo: true,
  displayType: true,
  displayDescription: true,
  displayMembership: true,
};

export default GroupCard;
