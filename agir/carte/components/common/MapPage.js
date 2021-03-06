import { Helmet } from "react-helmet";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";

const CONFIG = {
  events: {
    title: "Carte des événements",
    backLabel: "Liste des événements",
    backRoute: "events",
  },
  groups: {
    title: "Carte des groupes",
    backLabel: "Liste des groupes",
    backRoute: "groups",
  },
};
const Header = styled.header`
  width: 100%;
  height: 100px;
  text-align: center;
  position: relative;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: center;
  background-color: white;

  & > h1 {
    text-align: center;
    font-size: 1.25rem;
    line-height: 1.5;
    color: ${style.black1000};
    font-weight: 700;
    margin: 0;
  }

  & > ${Button} {
    position: absolute;
    left: 1.5rem;
    top: 50%;
    transform: translateY(-50%);

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  & > a:last-child {
    font-size: 13px;
  }
`;

const Map = styled.iframe`
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  height: calc(100vh - 172px);
  border: none;
  overflow: hidden;
`;

const MapPage = (props) => {
  const { user, type, mapURL, createLinkProps } = props;
  const { title, backRoute, backLabel } = CONFIG[type];

  return (
    <main>
      <Helmet>
        <title>{title} - Action populaire</title>
      </Helmet>
      <Header>
        {user && (
          <Button as="Link" route={backRoute} icon="arrow-left">
            <span>{backLabel}</span>
          </Button>
        )}
        <h1>{title}</h1>
        {user && <Link {...createLinkProps} />}
      </Header>
      <Map src={mapURL}></Map>
    </main>
  );
};

MapPage.propTypes = {
  user: PropTypes.object,
  type: PropTypes.oneOf(["events", "groups"]),
  backRoute: PropTypes.string,
  mapURL: PropTypes.string,
  createLinkProps: PropTypes.shape({
    as: PropTypes.oneOf(["Link", "a"]),
    href: PropTypes.string,
    to: PropTypes.string,
    route: PropTypes.string,
    children: PropTypes.string,
  }),
};
export default MapPage;
