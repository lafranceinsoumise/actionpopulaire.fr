import React from "react";
import Card from "../../../front/components/genericComponents/Card";
import PropTypes from "prop-types";

import Svg from "./group.svg";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import styles from "@agir/front/genericComponents/style.scss";
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const ResponsiveButton = styled(Button)`
  @media only screen and (max-width: 500px) {
    display: block;
  }
`;

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

const EventGroupCard = ({
  name,
  url,
  description,
  eventCount,
  membersCount,
  isMember,
  type,
  labels,
}) => (
  <>
    <Hide under style={{ marginBottom: "1rem", marginTop: "2.5rem" }}>
      <h3>Organisé par</h3>
    </Hide>
    <Card>
      <Hide over style={{ marginBottom: "1rem" }}>
        <h3>Organisé par</h3>
      </Hide>
      <Row gutter={6}>
        <Column collapse={0}>
          <img src={Svg} alt="Groupe" />
        </Column>
        <Column collapse={0} fill>
          <h3 style={{ marginTop: 2, marginBottom: 2 }}>
            <a href={url}>{name}</a>
          </h3>
          <small style={{ color: styles.black500 }}>
            {eventCount} événements • {membersCount} membres
          </small>
        </Column>
      </Row>

      <div style={{ marginTop: "24px" }}>
        <Label main>{type}</Label>
        {labels.map((label, index) => (
          <Label key={index}>{label}</Label>
        ))}
      </div>

      <div
        dangerouslySetInnerHTML={{ __html: description }}
        style={{ margin: "24px 0" }}
      />
      <Row gutter={6}>
        <Column width={["45%", "content"]} collapse={500}>
          <ResponsiveButton color="primary" as="a">
            Détails
          </ResponsiveButton>
        </Column>
        {!isMember && (
          <Column width={["55%", "content"]} collapse={500}>
            <ResponsiveButton as="a">
              Rejoindre
              <Hide as="span" under={800}>
                {" "}
                le groupe
              </Hide>
            </ResponsiveButton>
          </Column>
        )}
      </Row>
      {isMember && (
        <div style={{ marginTop: "1em" }}>
          <FeatherIcon small inline name="check" /> Vous êtes membre du groupe
        </div>
      )}
    </Card>
  </>
);

EventGroupCard.propTypes = {
  name: PropTypes.string,
  url: PropTypes.arrayOf(PropTypes.string),
  description: PropTypes.string,
  eventCount: PropTypes.number,
  membersCount: PropTypes.number,
  isMember: PropTypes.bool,
  type: PropTypes.string,
  labels: PropTypes.arrayOf(PropTypes.string),
};

export default EventGroupCard;
