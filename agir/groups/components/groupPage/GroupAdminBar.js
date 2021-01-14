import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";

const LeftSection = styled.div``;
const RightSection = styled.div``;
const InlineMenuList = styled.ul`
  cursor: pointer;
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  list-style: none;
  color: ${style.primary500};
  padding: 0;
  margin: 0;

  a,
  a:hover {
    font-size: 14px;
    line-height: 1.5;
    font-weight: 400;
    color: ${style.black1000};
  }
`;
const StyledBar = styled.nav`
  display: flex;
  flex-flow: row nowrap;
  height: 82px;
  align-items: center;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }

  ${LeftSection} {
    margin-right: auto;
  }
`;

const GroupAdminBar = (props) => {
  const { routes } = props;

  return (
    <StyledBar>
      <LeftSection>
        <Button as="a" href={routes.createEvent} color="primary" icon="plus">
          Créer un événement du groupe
        </Button>
      </LeftSection>
      <RightSection>
        {routes.settings && (
          <Button as="a" href={routes.settings} icon="settings">
            Paramètres
          </Button>
        )}
        {routes.members && (
          <Button as="a" href={routes.members} icon="users">
            Membres
          </Button>
        )}
      </RightSection>
      <InlineMenu>
        <InlineMenuList>
          {routes.animation && (
            <li>
              <FeatherIcon inline small name="settings" color={style.primary} />
              &ensp;
              <a href={routes.animation}>Animation</a>
            </li>
          )}
          {routes.membershipTransfer && (
            <li>
              <FeatherIcon inline small name="settings" color={style.primary} />
              &ensp;
              <a href={routes.membershipTransfer}>Transfer de membres</a>
            </li>
          )}
          {routes.admin && (
            <li>
              <FeatherIcon inline small name="settings" color={style.primary} />
              &ensp;
              <a href={routes.admin}>Administration</a>
            </li>
          )}
        </InlineMenuList>
      </InlineMenu>
    </StyledBar>
  );
};

GroupAdminBar.propTypes = {
  routes: PropTypes.shape({
    createEvent: PropTypes.string,
    settings: PropTypes.string,
    members: PropTypes.string,
    admin: PropTypes.string,
  }),
};
export default GroupAdminBar;
