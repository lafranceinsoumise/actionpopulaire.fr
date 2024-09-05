import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import defaultBackground from "@agir/front/genericComponents/images/event-card-default-bg.svg";
import Button from "@agir/front/genericComponents/Button";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledIllustration = styled.figure`
  padding: 0;
  margin: 0;
  background-color: ${({ $img, theme }) =>
    $img ? theme.text100 : theme.text25};
  display: grid;
  isolation: isolate;
  z-index: 0;
  width: 100%;
  max-width: 100%;

  & > * {
    grid-column: 1/2;
    grid-row: 1/2;
  }

  &::before {
    content: "";
    z-index: 0;
    grid-column: 1/2;
    grid-row: 1/2;
    display: block;
    height: 100%;
    width: 100%;
    background-image: url(${({ $img }) => $img || defaultBackground});
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      opacity: 0.25;
      background-size: ${({ $img }) => ($img ? "cover" : "auto 100%")};
      background-position: ${({ $img }) =>
        $img ? "top center" : "center center"};
    }
  }

  img {
    z-index: 1;
    height: inherit;
    visibility: hidden;
    margin: 0 auto;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      visibility: visible;
      align-self: center;
    }
  }
`;

const StyledCard = styled(Card).attrs({ bordered: true })`
  width: 100%;
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;
  border-radius: ${(props) => props.theme.borderRadius};

  @media (min-width: ${(props) => props.theme.collapse}px) {
    box-shadow: none;
    border: 1px solid ${(props) => props.theme.text100};
    min-height: 136px;
    flex-direction: row;
  }

  ${StyledIllustration} {
    flex: 0 0 320px;
    height: 256px;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex: 0 0 136px;
      height: 136px;
    }
  }

  & > div {
    flex: 1 1 auto;
    min-height: 256px;
    padding: 1rem;
    display: flex;
    flex-flow: column nowrap;

    h4 {
      font-weight: 700;
      font-size: 1rem;
      line-height: 2;
      text-transform: uppercase;
      margin: 0;
    }

    article {
      font-size: 0.875rem;
      line-height: 1.5;
      margin-bottom: 1rem;

      p {
        margin: 0 0 0.5rem;
      }
    }

    footer {
      margin-top: auto;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }
  }
`;

const ThematicGroupCard = (props) => {
  const { id, name, description, image, externalLink } = props;

  const isDesktop = useIsDesktop();

  return (
    <StyledCard>
      <StyledIllustration $img={image}>
        {image && <img src={image} alt="Image d'illustration" />}
      </StyledIllustration>
      <div>
        <h4>{name}</h4>
        <article dangerouslySetInnerHTML={{ __html: description }} />
        <footer>
          {externalLink && (
            <Button
              small={!isDesktop}
              link
              href={externalLink.url}
              color="choose"
              icon="external-link"
              target="_blank"
            >
              {externalLink.label}
            </Button>
          )}
          <Button
            small={!isDesktop}
            link
            route="groupDetails"
            routeParams={{ groupPk: id }}
            backLink="thematicGroups"
          >
            Rejoindre
          </Button>
        </footer>
      </div>
    </StyledCard>
  );
};

ThematicGroupCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  image: PropTypes.string,
  externalLink: PropTypes.shape({
    url: PropTypes.string,
    label: PropTypes.string,
  }),
};

export default ThematicGroupCard;
