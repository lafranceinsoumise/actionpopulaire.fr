import { Helmet } from "react-helmet";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";

const CONFIG = {
  events: {
    title: "Carte des événements",
    backLabel: "Liste des événements",
    createLabel: "Créer un événement dans mon quartier",
  },
  groups: {
    title: "Carte des groupes",
    backLabel: "Liste des groupes",
    createLabel: "Créer un groupe dans mon quartier",
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
  const { user, type, back, create, map } = props;
  const { title, backLabel, createLabel } = CONFIG[type];

  return (
    <main>
      <Helmet>
        <title>{title} - Action populaire</title>
      </Helmet>
      <Header>
        {user && back && (
          <Button as="a" href={back} icon="arrow-left">
            <span>{backLabel}</span>
          </Button>
        )}
        <h1>{title}</h1>
        {user && create && <a href={create}>{createLabel}</a>}
      </Header>
      <Map src={map}></Map>
    </main>
  );
};

MapPage.propTypes = {
  user: PropTypes.object,
  type: PropTypes.oneOf(["events", "groups"]),
  back: PropTypes.string,
  create: PropTypes.string,
  map: PropTypes.string,
};
export default MapPage;
