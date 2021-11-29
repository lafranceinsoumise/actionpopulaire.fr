import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import ActionButtons from "@agir/front/app/ActionButtons/ActionButtons";
import Announcements from "@agir/front/app/Announcements";
import FacebookLoginAd from "@agir/front/app/FacebookLoginAd";
import { LayoutTitle, LayoutSubtitle } from "./StyledComponents";
import SideBar, { SecondarySideBar } from "@agir/front/app/Navigation/SideBar";
import Spacer from "@agir/front/genericComponents/Spacer";
import UpcomingEvents from "@agir/events/common/UpcomingEvents";

const LeftColumn = styled.aside`
  position: sticky;
  top: 3rem;
  z-index: ${(props) => props.theme.zindexMainContent};
`;
const MainColumn = styled.div``;
const RightColumn = styled.aside``;

const MainContainer = styled.div`
  width: 100%;
  max-width: 1442px;
  margin: 0 auto;
  padding: 0 50px 3rem;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;

  ${LeftColumn} {
    padding: 3rem 2rem 0 0;
    flex: 0 0 255px;
    min-width: 1px;

    @media (max-width: ${(props) => props.theme.collapseTablet}px) {
      display: none;
    }
  }

  ${RightColumn} {
    padding: 3rem 0 0 2rem;
    flex: 0 0 255px;

    h4 {
      margin: 0 0 0.5rem;
      line-height: 1.5;
    }
  }

  ${MainColumn} {
    padding: 3rem 0 0;
    flex: 0 1 725px;
    margin: 0 auto;

    @media (max-width: ${(props) => props.theme.collapseTablet}px) {
      flex-grow: 1;
    }
  }
`;

const Layout = (props) => {
  const { title, subtitle, children } = props;

  const { data: events } = useSWR("/api/evenements/rsvped/");

  return (
    <MainContainer {...props}>
      <LeftColumn>
        <SideBar {...props} />
      </LeftColumn>
      <MainColumn>
        <section>
          {props.title ? (
            <header>
              <LayoutTitle>{title}</LayoutTitle>
              <LayoutSubtitle>{subtitle}</LayoutSubtitle>
            </header>
          ) : null}
          {children}
        </section>
      </MainColumn>
      <RightColumn>
        <div>
          <h4>Moyens d'action</h4>
          <ActionButtons />
        </div>
        <Spacer size="2rem" />
        {Array.isArray(events) && events.length > 0 ? (
          <>
            <div>
              <h4>Mes événements prévus</h4>
              <UpcomingEvents orientation="vertical" events={events} />
            </div>
            <Spacer size="2rem" />
          </>
        ) : null}
        <FacebookLoginAd />
        <Announcements />
        <SecondarySideBar />
      </RightColumn>
    </MainContainer>
  );
};

export default Layout;

Layout.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  children: PropTypes.node,
};
