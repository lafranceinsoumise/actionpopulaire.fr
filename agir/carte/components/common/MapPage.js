import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const CONFIG = {
  events: {
    backLabel: "Liste des événements",
    backRoute: "events",
  },
  groups: {
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
  background-color: white;
  padding: 0 20px;
  flex-direction: row;
  justify-content: space-between;

  & > h1 {
    text-align: center;
    font-size: 1.25rem;
    line-height: 1.5;
    color: ${style.black1000};
    font-weight: 700;
    margin: 0;
  }

  & > a:last-child {
    font-size: 13px;
  }
`;

const Map = styled.iframe`
  margin: 0;
  padding: 0;
  border: none;
  overflow: hidden;
  width: 100%;
  height: 100%;
  height: calc(100vh - 172px);
  display: block;
  @media (max-width: ${style.collapse}px) {
    height: calc(100vh - 138px);
  }
`;

const MapFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 82px;
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #fff;
`;

const StyledActionButtons = styled.div`
  min-width: 310px;
  display: inline-flex;
  justify-content: space-around;
`;

const ActionButtons = ({ searchUrl, createLinkProps }) => (
  <StyledActionButtons>
    <Button link href={searchUrl}>
      <RawFeatherIcon name="search" height="1rem" color={style.black1000} />
      &nbsp;Rechercher
    </Button>
    <Button color="secondary" link route={createLinkProps.route}>
      <RawFeatherIcon name="plus" height="1rem" color={style.black1000} />
      &nbsp;Créer
    </Button>
  </StyledActionButtons>
);

const MapPage = (props) => {
  const { user, type, mapURL, createLinkProps, searchUrl } = props;
  const { backRoute, backLabel } = CONFIG[type];

  return (
    <main>
      <Hide under as={Header}>
        {user && (
          <Button link route={backRoute} icon="arrow-left">
            <span>{backLabel}</span>
          </Button>
        )}
        <h1>{title}</h1>
        <ActionButtons
          searchUrl={searchUrl}
          createLinkProps={createLinkProps}
        />
      </Hide>
      <Map src={mapURL}></Map>
      <Hide over as={MapFooter}>
        <ActionButtons
          searchUrl={searchUrl}
          createLinkProps={createLinkProps}
        />
      </Hide>
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
