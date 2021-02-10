import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";
import Popin from "@agir/front/genericComponents/Popin";

const StyledPanel = styled.div`
  width: 100%;
  background-color: ${style.primary100};
  padding: 1.5rem;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }

  h6 {
    margin: 0;
    font-size: 1rem;
    line-height: 1;
    color: ${style.primary500};
    margin-bottom: 1rem;
    font-weight: bold;
  }

  && ul {
    margin-bottom: 0;

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
    @media (min-width: ${style.collapse}px) {
      display: none;
    }
  }
`;
const StyledContent = styled.div`
  padding: 0;
  display: flex;
  align-items: flex-start;
  flex-flow: column nowrap;
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    background-color: white;
    width: 100%;
    padding: 0 1rem 1.5rem;
    margin-bottom: 0;
    align-items: stretch;
    display: ${({ hideOnMobile }) => (hideOnMobile ? "none" : "flex")};
  }

  & > ${Button} {
    margin: 0;
    width: 100%;
    justify-content: center;
  }

  & > ${Button} + ${Button} {
    margin-top: 0.75rem;
  }

  p {
    margin-top: 0.5rem;
    font-weight: 500;
    font-size: 0.813rem;
    line-height: 1.5;
    color: ${style.black500};

    @media (max-width: ${style.collapse}px) {
      font-size: 0.688rem;
      font-weight: 400;
      color: ${style.black1000};
    }
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

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
  const openPopin = useCallback(() => setIsPopinOpen(true), []);
  const closePopin = useCallback(() => setIsPopinOpen(false), []);

  if (isManager) {
    return (
      <StyledContent>
        <StyledPanel>
          <h6>Gestion du groupe</h6>
          {routes.createEvent && (
            <Button
              as="a"
              href={routes.createEvent}
              color="primary"
              icon="plus"
              small
              inline
            >
              Créer un événement {is2022 ? "de l'équipe" : "du groupe"}
            </Button>
          )}
          <ul>
            {routes.members && (
              <li>
                <RawFeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="users"
                />
                <a href={routes.members}>Membres</a>
              </li>
            )}
            {routes.settings && (
              <li>
                <RawFeatherIcon
                  inline
                  small
                  name="file-text"
                  color={style.primary500}
                />
                <a href={routes.settings}>Informations</a>
              </li>
            )}
            {routes.members && (
              <li>
                <RawFeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="lock"
                />
                <a href={routes.members}>Animateur·ices et gestionnaires</a>
              </li>
            )}
            {routes.financement && (
              <li>
                <RawFeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="folder"
                />
                <a href={routes.financement}>Remboursement et dépense</a>
              </li>
            )}
            {routes.certification && (
              <li>
                <RawFeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="check-circle"
                />
                <a href={routes.certification}>Certification</a>
              </li>
            )}
            {routes.financement && (
              <li>
                <RawFeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="loader"
                />
                <a href={routes.financement}>Financement</a>
              </li>
            )}
            {routes.invitation && (
              <li>
                <RawFeatherIcon
                  small
                  inline
                  color={style.primary500}
                  name="users"
                />
                <a href={routes.invitation}>Inviter</a>
              </li>
            )}
            {routes.admin && (
              <li>
                <RawFeatherIcon
                  inline
                  small
                  name="settings"
                  color={style.primary500}
                />
                <a href={routes.admin}>Administration</a>
              </li>
            )}
          </ul>
        </StyledPanel>
        <Button
          as="a"
          href={routes.createEvent}
          color="primary"
          icon="plus"
          small
        >
          Créer un événement {is2022 ? "de l'équipe" : "du groupe"}
        </Button>
        <Button as="a" href={routes.settings} icon="settings" small>
          Gestion {is2022 ? "de l'équipe" : "du groupe"}
        </Button>
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
          <Button onClick={openPopin} color="default" icon="check">
            Vous êtes membre {is2022 ? "de l'équipe" : "du groupe"}
          </Button>
          <Popin isOpen={isPopinOpen} onDismiss={closePopin} position="bottom">
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
        <Button type="submit" color="success">
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
