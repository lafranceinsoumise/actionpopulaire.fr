import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

const StyledPanel = styled.div`
  width: 100%;
  background-color: ${(props) => props.theme.primary100};
  padding: 1.5rem;
  margin: 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }

  h6 {
    margin: 0;
    font-size: 1rem;
    line-height: 1;
    color: ${(props) => props.theme.primary500};
    margin-bottom: 1rem;
    font-weight: bold;
  }

  && ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      font-size: 0.813rem;
      line-height: 1.3;
      display: flex;
      align-items: baseline;

      a {
        color: ${(props) => props.theme.text1000};
        margin-left: 0.5rem;
      }
    }

    li + li {
      margin-top: 0.5rem;
    }

    li {
      align-items: center;
      font-weight: normal;
      font-size: 0.875rem;

      a {
        margin-left: 0.5rem;
      }

      ${RawFeatherIcon} {
        svg {
          stroke-width: 2px;
          width: 1rem;
          height: 1rem;
        }
      }
    }
  }

  ${Button} + ul {
    margin-top: 1rem;
  }

  & ~ ${Button} {
    @media (min-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }
`;

const StyledWrapper = styled.div`
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  position: relative;
`;

const ManagerActions = (props) => {
  const { id, groupSettingsLinks, isBoucleDepartementale } = props;

  return (
    <StyledWrapper>
      <StyledPanel>
        <h6>Gestion du groupe</h6>
        <Button
          link
          route="createEvent"
          params={{ group: id }}
          color="primary"
          icon="plus"
          small
        >
          Créer un événement du groupe
        </Button>
        <ul>
          {groupSettingsLinks?.members && (
            <li>
              <RawFeatherIcon color="primary500" name="users" />
              <Link to={groupSettingsLinks.members}>Membres</Link>
            </li>
          )}
          {groupSettingsLinks?.contacts && (
            <li>
              <RawFeatherIcon color="primary500" name="rss" />
              <Link to={groupSettingsLinks.contacts}>Contacts</Link>
            </li>
          )}
          {groupSettingsLinks?.general && (
            <li>
              <RawFeatherIcon color="primary500" name="file-text" />
              <Link to={groupSettingsLinks.general}>Informations</Link>
            </li>
          )}
          {groupSettingsLinks?.manage && (
            <li>
              <RawFeatherIcon color="primary500" name="lock" />
              <Link to={groupSettingsLinks.manage}>
                Animateur·ices et gestionnaires
              </Link>
            </li>
          )}
          {groupSettingsLinks?.finance && (
            <li>
              <RawFeatherIcon color="primary500" name="briefcase" />
              <Link to={groupSettingsLinks.finance}>
                {isBoucleDepartementale
                  ? "Caisse de la boucle"
                  : "Caisse du groupe"}
              </Link>
            </li>
          )}
          {groupSettingsLinks?.upcomingEvents && (
            <li>
              <RawFeatherIcon color="primary500" name="calendar" />
              <Link to={groupSettingsLinks.upcomingEvents}>Agenda</Link>
            </li>
          )}
          {groupSettingsLinks?.links && (
            <li>
              <RawFeatherIcon color="primary500" name="loader" />
              <Link to={groupSettingsLinks.links}>Liens externes</Link>
            </li>
          )}
          {groupSettingsLinks?.stats && (
            <li>
              <RawFeatherIcon color="primary500" name="trello" />
              <Link to={groupSettingsLinks.stats}>Statistiques</Link>
            </li>
          )}
        </ul>
      </StyledPanel>
      <Button link route="createEvent" color="primary" icon="plus" small>
        Créer un événement du groupe
      </Button>
      <Button link to={groupSettingsLinks?.menu} icon="settings" small>
        Gestion du groupe
      </Button>
    </StyledWrapper>
  );
};

ManagerActions.propTypes = {
  id: PropTypes.string.isRequired,
  routes: PropTypes.object,
  groupSettingsLinks: PropTypes.object,
  isBoucleDepartementale: PropTypes.string,
};
export default ManagerActions;
