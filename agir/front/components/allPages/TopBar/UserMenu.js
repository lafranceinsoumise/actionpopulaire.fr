import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";

import Avatar from "@agir/front/genericComponents/Avatar";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Button from "@agir/front/genericComponents/Button";
import Popin from "@agir/front/genericComponents/Popin";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import { routeConfig } from "@agir/front/app/routes.config";

const IconLink = styled(Link)``;
const StyledUserMenu = styled.div`
  margin: -1rem;
  padding: 1.5rem 0 0;
  text-align: center;
  cursor: default;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem 0;
    margin: 0 auto;
  }

  header {
    display: inline-flex;
    align-items: center;
    position: relative;
    padding: 0;
    margin: 0;

    ${Avatar} {
      width: 5rem;
      height: 5rem;
    }

    ${IconLink} {
      display: inline-flex;
      position: absolute;
      width: 2rem;
      height: 2rem;
      align-items: center;
      justify-content: center;
      top: 0;
      right: 0;
      transform: translateX(50%);
      background-color: ${style.white};
      outline: none;
      border: 1px solid ${style.black200};
      border-radius: 100%;
      transition: all 100ms ease-in-out;

      &:hover,
      &:focus {
        background-color: ${style.black25};
        border: 1px solid ${style.black100};
        cursor: pointer;
      }
    }
  }

  article {
    font-weight: 400;
    font-size: 0.875rem;
    line-height: 1.5;
    padding: 1rem 0;
    margin: 0;

    p {
      margin: 0;
      padding: 0;

      &:empty {
        display: none;
      }
    }

    strong {
      font-size: 1rem;
      font-weight: 600;
    }

    ${Button} {
      margin: 0.875rem 0 0;
    }
  }

  footer {
    margin: 0;
    padding: 1rem 0;
    border-top: 1px solid ${style.black100};

    ${Button} {
      margin: 0;
    }
  }
`;

export const UserMenu = (props) => {
  const { user } = props;
  const routeSettings = routeConfig.notificationSettings.getLink();

  return (
    <ResponsiveLayout
      MobileLayout={BottomSheet}
      DesktopLayout={Popin}
      noPadding
      {...props}
    >
      <StyledUserMenu>
        <header>
          <Avatar displayName={user.displayName} image={user.image} />
          <IconLink route="personalInformation">
            <RawFeatherIcon name="edit-2" width="1rem" height="1rem" />
          </IconLink>
        </header>
        <article>
          <p>
            <strong>{user.displayName}</strong>
          </p>
          {user.fullName !== user.email && <p>{user.fullName}</p>}
          <p>{user.email}</p>
          <Button
            as="Link"
            route="personalInformation"
            icon="settings"
            color="secondary"
            small
          >
            Paramètres
          </Button>
          <Button
            as="Link"
            route={routeSettings}
            icon="settings"
            color="secondary"
            small
          >
            Notifications et e-mail
          </Button>
        </article>
        <footer>
          <Button
            as="Link"
            route="logout"
            icon="power"
            $background={style.white}
            $labelColor={style.black1000}
            $hoverBackground={style.black25}
            $borderColor={style.black200}
            small
          >
            Me déconnecter
          </Button>
        </footer>
      </StyledUserMenu>
    </ResponsiveLayout>
  );
};
UserMenu.propTypes = {
  user: PropTypes.shape({
    displayName: PropTypes.string,
    fullName: PropTypes.string,
    email: PropTypes.string,
    image: PropTypes.string,
  }),
  isOpen: PropTypes.bool,
  onOpen: PropTypes.func,
  onDismiss: PropTypes.func,
};

export default UserMenu;
