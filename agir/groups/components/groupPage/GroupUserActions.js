import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Popin from "@agir/front/genericComponents/Popin";

const StyledPanel = styled.div`
  width: 100%;
  background-color: ${style.primary100};
  padding: 1.5rem;
  margin: 1rem 0;
`;
const StyledContent = styled.div`
  padding: 0;
  display: flex;
  align-items: flex-start;
  flex-flow: column nowrap;

  @media (max-width: ${style.collapse}px) {
    background-color: white;
    width: 100%;
    padding: 0 1rem;
    align-items: stretch;
    display: ${({ hideOnMobile }) => (hideOnMobile ? "none" : "flex")};
  }

  ${Button} {
    margin: 0;
    width: 100%;
    justify-content: center;
  }

  ${Button} + ${Button} {
    margin-top: 1rem;
  }

  p {
    font-weight: 500;
    font-size: 0.813rem;
    line-height: 1.5;
    color: ${style.black500};
    margin-top: 1em;

    @media (max-width: ${style.collapse}px) {
      font-size: 0.688rem;
      font-weight: 400;
      color: ${style.black1000};
    }
  }

  ul {
    list-style: none;
    padding: 0;

    li {
      font-size: 0.813rem;
      line-height: 1.3;
      display: flex;
      align-items: baseline;

      a {
        color: ${style.black1000};
        margin-left: 0.5rem;
      }
    }

    li + li {
      margin-top: 0.5rem;
    }
  }
`;

const GroupLinks = (props) => {
  const { isMember, isManager, is2022 = false, routes } = props;

  const [isPopinOpen, setIsPopinOpen] = useState(false);
  const togglePopinOpen = useCallback(
    () => setIsPopinOpen((state) => !state),
    []
  );

  if (isManager) {
    return (
      <StyledContent>
        <Button as="a" href={routes.createEvent} color="primary" icon="plus">
          Créer un événement {is2022 ? "de l'équipe" : "du groupe"}
        </Button>
        <Button as="a" href={routes.settings} color="primary" icon="settings">
          Gestion {is2022 ? "de l'équipe" : "du groupe"}
        </Button>
        <StyledPanel>
          <ul>
            {routes.invitation && (
              <li>
                <FeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="users"
                />
                <a href={routes.invitation}>Inviter un membre</a>
              </li>
            )}
            {routes.materiel && (
              <li>
                <FeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="shopping-bag"
                />
                <a href={routes.materiel}>Commander du matériel</a>
              </li>
            )}
            {routes.financement && (
              <li>
                <FeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="folder"
                />
                <a href={routes.settings}>Demande de dépense</a>
              </li>
            )}
            {routes.members && (
              <li>
                <FeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="lock"
                />
                <a href={routes.members}>Animateur·ices et gestionnaires</a>
              </li>
            )}
            {routes.admin && (
              <li>
                <FeatherIcon
                  inline
                  small
                  name="settings"
                  color={style.primary}
                />
                <a href={routes.admin}>Administration</a>
              </li>
            )}
          </ul>
        </StyledPanel>
      </StyledContent>
    );
  }

  if (isMember && routes.quit) {
    return (
      <StyledContent hideOnMobile>
        <div
          style={{
            width: "100%",
            position: "relative",
            margin: "0 0 1rem",
          }}
        >
          <Button onClick={togglePopinOpen} color="default" icon="check">
            Vous êtes membre {is2022 ? "de l'équipe" : "du groupe"}
          </Button>
          <Popin isOpen={isPopinOpen} position="bottom">
            <ul>
              <li>
                <FeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="users"
                />
                &emsp;
                <a href={routes.quit}>
                  Quitter {is2022 ? "l'équipe" : "le groupe"}
                </a>
              </li>
            </ul>
          </Popin>
        </div>
      </StyledContent>
    );
  }

  return (
    <StyledContent>
      <CSRFProtectedForm method="post" action={routes.join || ""}>
        <input type="hidden" name="action" value="join" />
        <Button type="submit" color="primary">
          Rejoindre {is2022 ? "l'équipe" : "le groupe"}
        </Button>
      </CSRFProtectedForm>
      <p>Votre email sera communiquée aux animateur-ices</p>
    </StyledContent>
  );
};

GroupLinks.propTypes = {
  isMember: PropTypes.bool,
  isManager: PropTypes.bool,
  is2022: PropTypes.bool,
  routes: PropTypes.object,
};
export default GroupLinks;
