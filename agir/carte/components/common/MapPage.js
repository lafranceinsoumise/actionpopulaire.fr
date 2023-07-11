import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";
import useSWR from "swr";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";

import nonReactRoutes from "@agir/front/globalContext/nonReactRoutes.config";
import {
  getDefaultBoundsForUser,
  getMapUrl,
  parseURLSearchParams,
} from "@agir/carte/map/utils";

const StyledActionButtons = styled.div`
  display: inline-flex;
  gap: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    position: fixed;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    padding: 0 1rem;
    height: 54px;
    background-color: ${(props) => props.theme.white};
    box-shadow: ${(props) => props.theme.elaborateShadow};
  }
`;

const TabLink = styled(Link)`
  display: flex;
  align-items: center;
  border-bottom: 2px solid transparent;
  color: ${(props) => props.theme.black1000};
  font-weight: 500;
  font-size: 0.875rem;
  line-height: 1;

  &:hover,
  &:focus {
    text-decoration: none;
    color: ${(props) => props.theme.black1000};
    border-color: ${(props) => props.theme.black1000};
  }

  &[disabled] {
    cursor: default;
    color: ${(props) => props.theme.primary500};
    border-color: ${(props) => props.theme.primary500};
  }
`;

const StyledTabLinks = styled.div`
  height: 100%;
  display: flex;
  align-items: stretch;
  gap: 2rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
    justify-content: center;
  }
`;

const Header = styled.header`
  width: 1432px;
  margin: 0 auto;
  padding: 0 50px;
  max-width: 100%;
  height: 60px;
  text-align: center;
  position: relative;
  display: flex;
  flex-flow: column nowrap;
  background-color: white;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: space-between;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    height: 54px;
    padding: 0 1rem;
    box-shadow: ${(props) => props.theme.elaborateShadow};
  }
`;

const StyledMap = styled.iframe`
  margin: 0;
  padding: 0;
  border: none;
  overflow: hidden;
  width: 100%;
  height: 100%;
  height: calc(100vh - 132px);
  display: block;
`;

const MAP_TYPE_CONFIG = {
  events: {
    mapBaseURL: nonReactRoutes.eventsMap,
    searchRoute: "searchEvent",
    createRoute: "createEvent",
    itemLabel: "un événement",
    tabLabel: "Événements",
    tabRoute: "eventMap",
  },
  groups: {
    mapBaseURL: nonReactRoutes.groupsMap,
    searchRoute: "searchGroup",
    createHref: nonReactRoutes.createGroup,
    itemLabel: "un groupe",
    tabLabel: "Groupes d'action",
    tabRoute: "groupMap",
  },
};

const MapPage = (props) => {
  const { type } = props;

  const { data: session } = useSWR("/api/session/");
  const user = session?.user;

  const { mapBaseURL, searchRoute, createRoute, createHref, itemLabel } =
    MAP_TYPE_CONFIG[type];

  const mapParams = useMemo(() => parseURLSearchParams(), [defaultBounds]);
  const defaultBounds = useMemo(() => getDefaultBoundsForUser(user), [user]);
  const mapSrc = useMemo(
    () => getMapUrl(mapBaseURL, defaultBounds),
    [mapBaseURL, defaultBounds]
  );

  return (
    <main>
      <Header>
        <StyledTabLinks>
          {Object.entries(MAP_TYPE_CONFIG).map(([typeId, config]) => (
            <TabLink
              key={typeId}
              disabled={type === typeId}
              route={config.tabRoute}
              params={mapParams}
            >
              {config.tabLabel}
            </TabLink>
          ))}
        </StyledTabLinks>
        <StyledActionButtons>
          <Button small link icon="search" route={searchRoute}>
            Rechercher
            <Hide as="span" under>
              &nbsp;{itemLabel}
            </Hide>
          </Button>
          <Button
            small
            link
            color="secondary"
            route={createRoute}
            href={createHref}
            icon="plus"
          >
            Créer
            <Hide as="span" under>
              &nbsp;{itemLabel}
            </Hide>
          </Button>
        </StyledActionButtons>
      </Header>
      <StyledMap src={mapSrc} />
    </main>
  );
};

MapPage.propTypes = {
  type: PropTypes.oneOf(["events", "groups"]),
};

export default MapPage;
