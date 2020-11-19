import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import {
  Column,
  Container,
  GrayBackground,
  Row,
} from "@agir/front/genericComponents/grid";
import Navigation from "@agir/front/dashboardComponents/Navigation";

export const LayoutTitle = styled.h1`
  font-size: 28px;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    margin: 0 25px;
    font-size: 20px;
  }
`;

const MainColumn = styled(Column)``;

const MainContainer = styled(Container)`
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  padding-top: 72px;
  padding-bottom: 72px;

  & > ${Row} > ${Column} {
    max-height: calc(100vh - 72px);
    overflow-x: hidden;
    overflow-y: auto;
    padding-top: 72px;

    @media (max-width: ${style.collapse}px) {
      padding-top: 0;
    }
  }

  & > ${Row} > ${MainColumn} {
    height: calc(100vh - 72px);

    @media (max-width: ${style.collapse}px) {
      padding-top: 0;
      padding-bottom: 100px;
      height: calc(100vh - 144px);
    }

    & > section {
      @media (min-width: ${style.collapse}px) {
        max-width: 711px;
      }
    }
  }
`;

const Layout = (props) => (
  <GrayBackground>
    <MainContainer>
      <Row gutter={72}>
        <Column>
          <Navigation {...props} />
        </Column>
        <MainColumn grow>
          <section>
            {props.title ? (
              <header>
                <LayoutTitle>{props.title}</LayoutTitle>
              </header>
            ) : null}
            {props.children}
          </section>
        </MainColumn>
      </Row>
    </MainContainer>
  </GrayBackground>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.oneOf(["events", "groups", "activity", "menu"]),
  routes: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          href: PropTypes.string,
        })
      ),
    ])
  ),
  title: PropTypes.string,
  children: PropTypes.node,
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
};
