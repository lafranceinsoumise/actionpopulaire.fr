import React, { useMemo } from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";

import MissingDocuments from "./MissingDocuments";

import { useMissingRequiredEventDocuments } from "@agir/events/common/hooks";

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

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

const StyledPage = styled.main`
  max-width: 716px;
  width: 100%;
  padding: 3rem;
  margin: 0 auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
    padding: 1.5rem;
    margin: 0;
    min-height: 100%;
  }
`;

const MissingDocumentsPage = () => {
  const { projects } = useMissingRequiredEventDocuments();

  const isBlocked = useMemo(() => {
    if (!Array.isArray(projects) || projects.length === 0) {
      return false;
    }
    return projects.some((project) => project.isBlocking);
  }, [projects]);

  return (
    <StyledPage>
      <IndexLinkAnchor route="events">
        <span>&#10140;</span>
        &ensp; Liste des événements
      </IndexLinkAnchor>
      <MissingDocuments projects={projects} isBlocked={isBlocked} />
    </StyledPage>
  );
};

export default MissingDocumentsPage;
