import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import googleLogo from "@agir/events/eventPage/assets/Google.svg";
import outlookLogo from "@agir/events/eventPage/assets/Outlook.svg";

import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Popin from "@agir/front/genericComponents/Popin";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import { slugify } from "@agir/lib/utils/url";

const LogoIcon = styled.span`
  display: inline-block;
  width: 1rem;
  height: 1rem;
  background-position: center center;
  background-size: cover;
  background-image: url(${(props) => props.$icon});
`;
const CalendarLink = styled.a``;
const StyledMenuList = styled.div`
  cursor: pointer;
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  align-items: stretch;
  list-style: none;
  padding: 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0;
    padding: 1.5rem;
    gap: 0.75rem;
  }

  ${CalendarLink} {
    color: ${(props) => props.theme.black1000};
    display: flex;
    align-items: center;
    font-weight: 400;
    font-size: 0.875rem;
    line-height: 1.5;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1rem;
    }

    &:focus,
    &:hover {
      outline: none;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        text-decoration: none;
      }
    }

    ${LogoIcon}, ${RawFeatherIcon} {
      color: ${(props) => props.theme.primary500};
      margin-right: 0.5rem;
    }
  }
`;

const StyledWrapper = styled.div`
  display: inline-block;
  position: relative;

  & > button {
    cursor: pointer;
    background-color: transparent;
    border: none;
    color: ${(props) => props.theme.primary500};
    font-weight: 500;
    display: inline-flex;
    align-items: center;

    ${RawFeatherIcon} {
      @media (max-width: ${(props) => props.theme.collapse}px) {
        display: none;
      }
    }
  }
`;

const AddToCalendarWidget = ({ name, routes }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const openMenu = () => setIsMenuOpen(true);
  const closeMenu = () => setIsMenuOpen(false);

  return (
    <StyledWrapper>
      <button onClick={openMenu} color="link">
        Ajouter à mon agenda&ensp;
        <RawFeatherIcon name="chevron-down" width="1rem" height="1rem" />
      </button>
      <ResponsiveLayout
        MobileLayout={BottomSheet}
        DesktopLayout={Popin}
        isOpen={isMenuOpen}
        onDismiss={closeMenu}
        position="bottom"
        shouldDismissOnClick
      >
        <StyledMenuList>
          <CalendarLink href={routes.googleExport}>
            <LogoIcon aria-hidden="true" $icon={googleLogo} />
            Sur Google Agenda
          </CalendarLink>
          <CalendarLink href={routes.calendarExport}>
            <LogoIcon aria-hidden="true" $icon={outlookLogo} />
            Sur Outlook
          </CalendarLink>
          <CalendarLink href={routes.calendarExport} download={slugify(name)}>
            <RawFeatherIcon
              aria-hidden="true"
              name="download"
              width="1rem"
              height="1rem"
            />
            Télécharger le .ics
          </CalendarLink>
        </StyledMenuList>
      </ResponsiveLayout>
    </StyledWrapper>
  );
};

AddToCalendarWidget.propTypes = {
  name: PropTypes.string,
  routes: PropTypes.shape({
    googleExport: PropTypes.string,
    calendarExport: PropTypes.string,
  }),
};
export default AddToCalendarWidget;
