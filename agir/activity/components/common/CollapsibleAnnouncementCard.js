import PropTypes from "prop-types";
import React, { useState } from "react";
import { animated, useSpring } from "@react-spring/web";
import { usePrevious } from "react-use";
import styled from "styled-components";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { useLocalStorage, useMeasure } from "@agir/lib/utils/hooks";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledHeader = styled.button`
  background-color: transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
  border: none;
  outline: none;
  cursor: pointer;
  width: 100%;
  height: 64px;
  padding: 0;
  margin: 0;

  span {
    transform-origin: "center center";
    line-height: 0;
  }
`;

const StyledBody = styled(animated.div)`
  padding: 0;
  margin: 0;
`;
const StyledFooter = styled(animated.footer)`
  padding: 0.5rem 0 1.5rem;

  ${Button} {
    @media (max-width: ${(props) => props.theme.collapse}px) {
      width: 100%;
    }
  }
`;
const StyledCard = styled(animated.div)`
  padding: 0 1.5rem;
  background-color: ${(props) => props.theme.secondary100};
  overflow: hidden;
  margin-bottom: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin-top: 1rem;
  }
`;

export const CollapsibleAnnouncementCard = (props) => {
  const { isInitiallyCollapsed, config, onClose } = props;
  const [isCollapsed, setIsCollapsed] = useState(isInitiallyCollapsed);
  const wasCollapsed = usePrevious(isCollapsed);

  const open = () => setIsCollapsed(false);
  const close = () => {
    onClose();
    setIsCollapsed(true);
  };

  const [bind, { height: viewHeight }] = useMeasure();

  const { height, opacity, transform } = useSpring({
    height: isCollapsed ? 64 : viewHeight,
    opacity: isCollapsed ? 0.33 : 1,
    transform: isCollapsed ? "rotate(0deg)" : "rotate(180deg)",
    config: {
      mass: 1,
      tension: 270,
      friction: !isCollapsed ? 26 : 36,
      clamp: true,
    },
  });

  return (
    <StyledCard
      style={{
        // Prevent animation if initially opened
        height: !isCollapsed && wasCollapsed === isCollapsed ? "auto" : height,
      }}
    >
      <div {...bind}>
        <StyledHeader type="button" onClick={isCollapsed ? open : close}>
          <strong>{config.title}</strong>
          <animated.span style={{ transform }}>
            <RawFeatherIcon name="chevron-down" />
          </animated.span>
        </StyledHeader>
        <StyledBody style={{ opacity }}>
          <div dangerouslySetInnerHTML={{ __html: config.content }} />
        </StyledBody>
        <StyledFooter style={{ opacity }}>
          <Button
            tabIndex={isCollapsed ? "-1" : undefined}
            type="button"
            color="secondary"
            onClick={close}
          >
            Compris
          </Button>
        </StyledFooter>
      </div>
    </StyledCard>
  );
};
CollapsibleAnnouncementCard.propTypes = {
  isInitiallyCollapsed: PropTypes.bool,
  onClose: PropTypes.func,
  config: PropTypes.object,
};

const HookedCollapsibleAnnouncementCard = ({ slug, ...rest }) => {
  const [announcementData] = useCustomAnnouncement(slug, false);
  const [isInitiallyCollapsed, setIsInitiallyCollapsed] = useLocalStorage(
    `AP__cac__${slug}`,
    false
  );
  const handleClose = () => setIsInitiallyCollapsed(true);

  return !!announcementData ? (
    <CollapsibleAnnouncementCard
      {...rest}
      isInitiallyCollapsed={isInitiallyCollapsed}
      config={announcementData}
      onClose={handleClose}
    />
  ) : null;
};
HookedCollapsibleAnnouncementCard.propTypes = {
  slug: PropTypes.string.isRequired,
};

export default HookedCollapsibleAnnouncementCard;
