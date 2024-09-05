import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled, { useTheme } from "styled-components";

import { getGroupTypeWithLocation } from "./utils";

import Map from "@agir/carte/common/Map";
import Modal from "@agir/front/genericComponents/Modal";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import GroupLocation from "@agir/groups/groupPage/GroupLocation";

import defaultGroupImage from "@agir/front/genericComponents/images/banner-map-background.svg";

const StyledModalBody = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  max-width: 600px;
  padding: 0;
  margin: 100px auto 0;
  background-color: ${(props) => props.theme.background0};
  box-shadow: ${(props) => props.theme.elaborateShadow};
  border-radius: ${(props) => props.theme.borderRadius};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: calc(100% - 20px);
    margin: 10px auto 0;
    padding-bottom: 10px;
  }

  && > * {
    border: none;
    box-shadow: none;
    margin: 0;
  }

  && > button {
    display: inline-flex;
    width: 2.5rem;
    height: 2.5rem;
    flex: 0 0 2.5rem;
    align-self: flex-end;
    background: none;
    cursor: pointer;
    color: ${(props) => props.theme.text1000};

    &:hover {
      opacity: 0.75;
    }
  }

  && > button + * {
    padding-top: 0;
    padding-bottom: 2.5rem;
  }
`;
const StyledGroupImage = styled.div``;
const StyledMap = styled.div``;
const StyledBanner = styled.div`
  display: flex;
  flex-flow: row-reverse nowrap;
  background-color: ${(props) => props.theme.secondary500};
  margin: 0 auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
    flex-flow: column nowrap;
    background-color: ${(props) => props.theme.background0};
  }

  header {
    flex: 1 1 auto;
    padding: 2.25rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 1.5rem 1.5rem 1.25rem;
      text-align: center;
    }
  }

  h2,
  h4 {
    margin: 0;
    &::first-letter {
      text-transform: uppercase;
    }
  }

  h2 {
    font-weight: 700;
    font-size: 1.75rem;
    line-height: 1.419;
    margin-bottom: 0.5rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.25rem;
      line-height: 1.519;
    }
  }

  h4 {
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.5;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.875rem;
    }

    button {
      background-color: transparent;
      font-size: inherit;
      line-height: inherit;
      font-weight: inherit;
      padding: 0;
      margin: 0;
      outline: none;
      border: none;
      cursor: pointer;
      text-decoration: underline;
    }
  }

  ${StyledMap} {
    flex: 0 0 424px;
    clip-path: polygon(100% 0%, 100% 100%, 0% 100%, 11% 0%);
    position: relative;
    background-size: 0 0;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      clip-path: none;
      width: 100%;
      height: 155px;
      flex-basis: 155px;
      background-size: contain;
      background-position: center center;
      background-repeat: no-repeat;
    }

    & > * {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100%;
      height: 100%;
    }

    ${StyledGroupImage} {
      background-position: center center;
      background-repeat: no-repeat;
      background-size: contain;

      &:first-child {
        background-size: cover;
        opacity: 0.2;
      }
    }
  }
`;

const GroupBanner = (props) => {
  const { name, typeLabel, location, iconConfiguration, image } = props;

  const theme = useTheme();
  const [shouldShowModal, setShouldShowModal] = useState();

  const subtitle = useMemo(
    () => getGroupTypeWithLocation(typeLabel, location),
    [typeLabel, location],
  );

  const openModal = useCallback(() => {
    setShouldShowModal(true);
  }, []);

  const closeModal = useCallback(() => {
    setShouldShowModal(false);
  }, []);

  const hasLocation = !!location;
  const hasMap =
    location?.coordinates && Array.isArray(location?.coordinates?.coordinates);

  return (
    <StyledBanner>
      <StyledMap
        onClick={hasMap && !image ? openModal : undefined}
        style={{
          backgroundColor: image ? theme.background0 : theme.secondary500,
          backgroundImage: !image ? `url(${defaultGroupImage})` : undefined,
          cursor: hasMap && !image ? "pointer" : "default",
        }}
      >
        {image ? (
          <>
            <StyledGroupImage
              aria-hidden="true"
              style={{ backgroundImage: `url(${image})` }}
            />
            <StyledGroupImage
              aria-hidden="true"
              style={{ backgroundImage: `url(${image})` }}
            />
          </>
        ) : hasMap ? (
          <Map
            zoom={11}
            center={location.coordinates.coordinates}
            iconConfiguration={iconConfiguration}
            isStatic
            staticMapUrl={location?.staticMapUrl}
          />
        ) : null}
      </StyledMap>
      {hasLocation && (
        <Modal shouldShow={shouldShowModal} onClose={closeModal} noScroll>
          <StyledModalBody>
            <button onClick={closeModal} aria-label="Fermer">
              <RawFeatherIcon name="x" width="1.5rem" heigth="1.5rem" />
            </button>
            <GroupLocation {...props} />
          </StyledModalBody>
        </Modal>
      )}
      <header>
        <h2>{name}</h2>
        <h4>{subtitle}</h4>
      </header>
    </StyledBanner>
  );
};
GroupBanner.propTypes = {
  name: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  typeLabel: PropTypes.string.isRequired,
  image: PropTypes.string,
  iconConfiguration: PropTypes.object,
  location: PropTypes.shape({
    name: PropTypes.string,
    address1: PropTypes.string,
    address2: PropTypes.string,
    city: PropTypes.string,
    zip: PropTypes.string,
    state: PropTypes.string,
    country: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
    staticMapUrl: PropTypes.string,
    commune: PropTypes.shape({
      nameOf: PropTypes.string,
    }),
  }),
};
export default GroupBanner;
