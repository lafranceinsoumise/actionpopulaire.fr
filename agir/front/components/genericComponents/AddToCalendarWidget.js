import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import googleLogo from "@agir/front/genericComponents/images/Google.svg";
import outlookLogo from "@agir/front/genericComponents/images/Outlook.svg";

import { useMobileApp } from "@agir/front/app/hooks";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Popin from "@agir/front/genericComponents/Popin";
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
    color: ${(props) => props.theme.text1000};
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

  ${Button} {
    font-weight: 500;
  }
`;

const AddToCalendarWidget = (props) => {
  const { children = "Ajouter à mon agenda", name, routes } = props;
  const { isIOS } = useMobileApp();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const openMenu = () => setIsMenuOpen(true);
  const closeMenu = () => setIsMenuOpen(false);

  if (!routes?.googleExport && !routes?.calendarExport) {
    return null;
  }

  return (
    <StyledWrapper>
      <Button onClick={openMenu} color="link" icon="chevron-down" rightIcon>
        {children}
      </Button>
      <ResponsiveLayout
        MobileLayout={BottomSheet}
        DesktopLayout={Popin}
        isOpen={isMenuOpen}
        onDismiss={closeMenu}
        position="bottom"
        shouldDismissOnClick
      >
        <StyledMenuList>
          {routes.googleExport && (
            <CalendarLink href={routes.googleExport}>
              <LogoIcon aria-hidden="true" $icon={googleLogo} />
              Sur Google Agenda
            </CalendarLink>
          )}
          {routes.calendarExport && (
            <>
              <CalendarLink href={routes.calendarExport}>
                <LogoIcon aria-hidden="true" $icon={outlookLogo} />
                Sur Outlook
              </CalendarLink>
              {isIOS ? (
                <CalendarLink
                  href={routes.calendarExport}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <RawFeatherIcon
                    a
                    ria-hidden="true"
                    name="download"
                    width="1rem"
                    height="1rem"
                  />
                  Télécharger le .ics
                </CalendarLink>
              ) : (
                <CalendarLink
                  href={routes.calendarExport}
                  download={slugify(name) + ".ics"}
                >
                  <RawFeatherIcon
                    aria-hidden="true"
                    name="download"
                    width="1rem"
                    height="1rem"
                  />
                  Télécharger le .ics
                </CalendarLink>
              )}
            </>
          )}
        </StyledMenuList>
      </ResponsiveLayout>
    </StyledWrapper>
  );
};

AddToCalendarWidget.propTypes = {
  children: PropTypes.node,
  name: PropTypes.string,
  routes: PropTypes.shape({
    googleExport: PropTypes.string,
    calendarExport: PropTypes.string,
  }),
};
export default AddToCalendarWidget;
