import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import Announcements from "@agir/front/dashboardComponents/Announcements";
import FacebookLoginAd from "@agir/front/dashboardComponents/FacebookLoginAd";
import Navigation, {
  SecondaryNavigation,
} from "@agir/front/dashboardComponents/Navigation";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import ActionButtons from "@agir/front/app/ActionButtons";
import { LayoutTitle, LayoutSubtitle } from "./StyledComponents";
import UpcomingEvents from "@agir/events/common/UpcomingEvents";

const FixedColumn = styled(Column)`
  position: sticky;
  top: 4.5rem;
  padding-top: 4.5rem;
  z-index: ${(props) => props.theme.zindexMainContent};
`;

const SidebarColumn = styled(Column)`
  padding-top: 4.5rem;
`;

const MainColumn = styled(Column)`
  padding-top: 4.5rem;
`;

const MainContainer = styled(Container)`
  padding-bottom: 4.5rem;

  & > ${Row} {
    flex-wrap: nowrap;
  }
`;

const Layout = (props) => {
  const { title, subtitle, children } = props;

  const { data: events } = useSWR("/api/evenements/rsvped/");

  return (
    <MainContainer {...props}>
      <Row gutter={50} align="flex-start">
        <FixedColumn width="320px">
          <Navigation {...props} />
        </FixedColumn>
        <MainColumn grow>
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
        <SidebarColumn>
          <div style={{ margin: "0 0 2rem" }}>
            <h4 style={{ margin: "0 0 .5rem" }}>Mes actions</h4>
            <ActionButtons />
          </div>
          {Array.isArray(events) && events.length > 0 ? (
            <div style={{ margin: "0 0 2rem" }}>
              <h4 style={{ lineHeight: 1.5, margin: "0 0 .5rem" }}>
                Mes événements prévus
              </h4>
              <UpcomingEvents orientation="vertical" events={events} />
            </div>
          ) : null}
          <FacebookLoginAd />
          <Announcements />
          <SecondaryNavigation />
        </SidebarColumn>
      </Row>
    </MainContainer>
  );
};

export default Layout;

Layout.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  children: PropTypes.node,
};
