import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import Footer from "@agir/front/dashboardComponents/Footer";

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin: 0 0 2rem;

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }

  span {
    transform: rotate(180deg) translateY(-1.5px);
    transform-origin: center center;
  }

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

export const LayoutTitle = styled.h1`
  text-align: center;
  font-size: 26px;
  line-height: 1.5;
  margin: 0 0 1rem;
  font-weight: 700;

  @media (max-width: ${style.collapse}px) {
    font-size: 20px;
    padding: 0 1.5rem;
  }
`;

const MainColumn = styled(Column)`
  padding-top: 72px;
  margin: 0 auto;
  max-width: 580px;

  @media (max-width: ${style.collapse}px) {
    max-width: 100%;
    padding-top: 0;
  }

  & > section > header {
    text-align: center;

    & > * + * {
      margin-top: 1rem;
    }
  }
`;

const MainContainer = styled(Container)`
  padding-bottom: 72px;
  @media (min-width: ${style.collapse}px) {
    & > ${Row} {
      flex-wrap: nowrap;
    }
  }
  @media (max-width: ${style.collapse}px) {
    padding-top: 24px;
    background-color: ${({ smallBackgroundColor }) =>
      smallBackgroundColor || "transparent"};
  }
`;

const CenteredLayout = (props) => (
  <>
    <MainContainer {...props}>
      <Row align="center">
        <MainColumn grow>
          {!!props.backLink && (
            <section>
              <IndexLinkAnchor
                to={props.backLink.to}
                href={props.backLink.href}
                route={props.backLink.route}
              >
                <span>&#10140;</span>
                &ensp; {props.backLink.label || "Retour à l'accueil"}
              </IndexLinkAnchor>
            </section>
          )}
          <section>
            <header>
              {props.icon ? (
                <RawFeatherIcon
                  name={props.icon}
                  width="2rem"
                  height="2rem"
                  color={style.primary500}
                />
              ) : null}
              {props.title ? <LayoutTitle>{props.title}</LayoutTitle> : null}
            </header>
            {props.children}
          </section>
        </MainColumn>
      </Row>
    </MainContainer>
    <Footer desktopOnly={props.desktopOnlyFooter} />
  </>
);

export default CenteredLayout;

CenteredLayout.propTypes = {
  icon: PropTypes.string,
  active: PropTypes.oneOf([
    "events",
    "groups",
    "activity",
    "required-activity",
    "menu",
  ]),
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
  subtitle: PropTypes.string,
  children: PropTypes.node,
  desktopOnlyFooter: PropTypes.bool,
  hasBanner: PropTypes.bool,
  backLink: PropTypes.shape({
    to: PropTypes.string,
    href: PropTypes.string,
    route: PropTypes.string,
    label: PropTypes.string,
  }),
};
CenteredLayout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
  desktopOnlyFooter: true,
  hasBanner: false,
};
