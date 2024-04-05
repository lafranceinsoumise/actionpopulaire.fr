import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import BackLink from "@agir/front/app/Navigation/BackLink";

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
  max-width: 100%;

  @media (max-width: ${style.collapse}px) {
    padding-top: 0;
  }

  & > section {
    &:empty {
      display: none;
    }

    & > header {
      text-align: center;

      & > * + * {
        margin-top: 1rem;
      }
    }
  }
`;

const MainContainer = styled(Container)`
  padding-bottom: 72px;

  @media (min-width: ${style.collapse}px) {
    max-width: ${({ $maxWidth }) => $maxWidth || "580px"};

    & > ${Row} {
      flex-wrap: nowrap;
    }
  }
  @media (max-width: ${style.collapse}px) {
    padding-top: 24px;
    background-color: ${({ $smallBackgroundColor }) =>
      $smallBackgroundColor || "transparent"};
  }
`;

const CenteredLayout = (props) => (
  <MainContainer {...props}>
    <Row align="center">
      <MainColumn grow>
        <section style={{ marginBottom: "2rem" }}>
          <BackLink style={{ margin: 0 }} />
        </section>
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
);

export default CenteredLayout;

CenteredLayout.propTypes = {
  icon: PropTypes.string,
  active: PropTypes.oneOf(["events", "groups", "activity", "menu"]),
  routes: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          href: PropTypes.string,
        }),
      ),
    ]),
  ),
  title: PropTypes.string,
  subtitle: PropTypes.string,
  children: PropTypes.node,
};
CenteredLayout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
};
