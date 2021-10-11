import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import ActionButtons from "@agir/front/app/ActionButtons";
import Announcements from "@agir/front/dashboardComponents/Announcements";
import FacebookLoginAd from "@agir/front/dashboardComponents/FacebookLoginAd";
import { LayoutTitle, LayoutSubtitle } from "./StyledComponents";
import Navigation, {
  SecondaryNavigation,
} from "@agir/front/dashboardComponents/Navigation";
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
    padding: 3rem 0 0;
    flex: 0 0 180px;
  }

  ${RightColumn} {
    padding: 3rem 0 0;
    flex: 0 0 255px;

    h4 {
      margin: 0 0 0.5rem;
      line-height: 1.5;
    }
  }

  ${MainColumn} {
    padding: 3rem 2rem 0;
    flex: 1 1 800px;
    max-width: 800px;
    margin: 0 auto;
  }
`;

const Layout = (props) => {
  const { title, subtitle, children } = props;

  const { data: events } = useSWR("/api/evenements/rsvped/");

  return (
    <MainContainer {...props}>
      <LeftColumn>
        <Navigation {...props} />
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
          <h4>Mes actions</h4>
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
        <SecondaryNavigation />
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
