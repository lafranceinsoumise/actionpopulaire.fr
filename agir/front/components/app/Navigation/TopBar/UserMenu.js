import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";

import Avatar from "@agir/front/genericComponents/Avatar";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { useColorScheme } from "@agir/front/theme/ThemeProvider";

const IconLink = styled(Link)``;
const StyledLink = styled(Link)``;
const StyledUserMenu = styled.div`
  width: 250px;
  margin: -1rem;
  padding: 1.5rem 0 0;
  text-align: center;
  cursor: default;

  @media (max-width: ${(props) => props.theme.collapse}px) {
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
      background-color: ${(props) => props.theme.background0};
      outline: none;
      border: 1px solid ${(props) => props.theme.text200};
      border-radius: 100%;
      transition: all 100ms ease-in-out;

      &:hover,
      &:focus {
        background-color: ${(props) => props.theme.text25};
        border: 1px solid ${(props) => props.theme.text100};
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

    ${StyledLink} {
      display: block;
      color: ${(props) => props.theme.text1000};
      margin: 0;
      padding: 0;

      &:hover,
      &:focus {
        text-decoration: none;
      }

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
    padding: 0.5rem 0;
    border-top: 1px solid ${(props) => props.theme.text100};
    font-size: 10px;
    color: ${(props) => props.theme.text500};
  }

  ${Button} {
    width: 230px;
  }
`;

const ColorModeToggle = (props) => {
  const [colorScheme, setColorScheme, colorSchemeChoice] = useColorScheme();

  return (
    <div
      css={`
        display: flex;
        gap: 0.5rem;
        padding-inline: 0.5rem;
        justify-content: center;

        & > ${Button} {
          flex: 0 0 2.5rem;
          height: 2.5rem;
          border-radius: 100%;

          & span:empty {
            display: none;
          }
        }
      `}
    >
      <Button
        small
        type="button"
        onClick={() => setColorScheme("light")}
        disabled={colorSchemeChoice === "light"}
        color={colorSchemeChoice === "light" ? "primary" : "confirmed"}
        title="Couleurs claires"
        icon="sun"
      ></Button>
      <Button
        small
        type="button"
        onClick={() => setColorScheme("dark")}
        disabled={colorSchemeChoice === "dark"}
        color={colorSchemeChoice === "dark" ? "primary" : "confirmed"}
        title="Couleurs sombres"
        icon="moon"
      ></Button>
      <Button
        small
        type="button"
        onClick={() => setColorScheme("auto")}
        disabled={colorSchemeChoice === "auto"}
        color={colorSchemeChoice === "auto" ? "primary" : "confirmed"}
        title="Couleurs par défaut"
        icon="monitor"
      ></Button>
    </div>
  );
};

export const UserMenu = (props) => {
  const { user } = props;

  return (
    <StyledUserMenu>
      <header>
        <Avatar displayName={user.displayName} image={user.image} />
        <IconLink route="personalInformation">
          <RawFeatherIcon name="edit-2" width="1rem" height="1rem" />
        </IconLink>
      </header>
      <article>
        <StyledLink route="personalInformation">
          <strong>{user.displayName}</strong>
        </StyledLink>
        {user.fullName !== user.email && (
          <StyledLink route="personalInformation">{user.fullName}</StyledLink>
        )}
        <StyledLink route="personalInformation">{user.email}</StyledLink>
        <StyledLink
          route="personalInformation"
          css={`
            color: ${(props) => props.theme.text500};
            line-height: 2;
          `}
        >
          {`${user.zip} ${user.city}`.trim()}
        </StyledLink>
        <ColorModeToggle />
        <Button
          link
          route="personalInformation"
          icon="settings"
          color="secondary"
          small
        >
          Paramètres
        </Button>
        <br />
        <Button
          link
          route="notificationSettings"
          icon="settings"
          color="secondary"
          small
        >
          Notifications et e-mails
        </Button>
        <br />
        <Button link route="logout" icon="power" color="choose" small>
          Me déconnecter
        </Button>
      </article>
      <footer>
        Version :{" "}
        {process.env.NODE_ENV === "production"
          ? process.env.SENTRY_RELEASE.slice(0, 7)
          : "development"}
      </footer>
    </StyledUserMenu>
  );
};
UserMenu.propTypes = {
  user: PropTypes.shape({
    displayName: PropTypes.string,
    fullName: PropTypes.string,
    email: PropTypes.string,
    image: PropTypes.string,
    zip: PropTypes.string,
    city: PropTypes.string,
  }),
};

export default UserMenu;
