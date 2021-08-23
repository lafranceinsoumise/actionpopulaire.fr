import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import Spacer from "@agir/front/genericComponents/Spacer";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import RightLinks from "./RightLinks";
import SearchBar from "./SearchBar";
import AdminLink from "./AdminLink";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getAdminLink, getUser } from "@agir/front/globalContext/reducers";
import { useUnreadActivityCount } from "@agir/activity/common/hooks";
import { useUnreadMessageCount } from "@agir/msgs/common/hooks";

const LogoLink = styled(Link)`
  line-height: 0;
  overflow-x: hidden;

  img {
    transform: translateX(-15px);
  }
`;
const StyledBar = styled.div`
  width: 1432px;
  max-width: 100%;
  height: 100%;
  background-color: ${(props) => props.theme.white};
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: flex-start;
  padding: 0 50px;
  position: relative;

  & > * {
    flex: 0 0 auto;
  }

  & > ${Button} {
    height: 2.5rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 0.5rem;
  }
`;

export const DesktopNavBar = (props) => {
  const { user, path, unreadMessageCount, unreadActivityCount, adminLink } =
    props;

  const createEventLabel = useResponsiveMemo(
    "Créer",
    "Créer un événement",
    1060
  );

  return (
    <>
      <AdminLink link={adminLink} />
      <StyledBar>
        <LogoLink route="events">
          <LogoAP height={56} width={149} />
        </LogoLink>
        {!!user && (
          <>
            <Button
              small
              link
              color="secondary"
              route="createEvent"
              icon="plus"
            >
              {createEventLabel}
            </Button>
            <Spacer size="1rem" />
          </>
        )}
        <div style={{ flex: "1 1 auto", maxWidth: 412 }}>
          <SearchBar isConnected={!!user} />
        </div>
        <Spacer size="1rem" />
        <RightLinks
          user={user}
          path={path}
          unreadMessageCount={unreadMessageCount}
          unreadActivityCount={unreadActivityCount}
        />
      </StyledBar>
    </>
  );
};
DesktopNavBar.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  path: PropTypes.string,
  unreadMessageCount: PropTypes.number,
  unreadActivityCount: PropTypes.number,
  adminLink: PropTypes.object,
};

const ConnectedDesktopNavBar = (props) => {
  const adminLink = useSelector(getAdminLink);
  const user = useSelector(getUser);
  const unreadMessageCount = useUnreadMessageCount();
  const unreadActivityCount = useUnreadActivityCount();

  return (
    <DesktopNavBar
      {...props}
      user={user}
      unreadMessageCount={unreadMessageCount}
      unreadActivityCount={unreadActivityCount}
      adminLink={adminLink}
    />
  );
};

ConnectedDesktopNavBar.propTypes = {
  path: PropTypes.string,
};

export default ConnectedDesktopNavBar;
