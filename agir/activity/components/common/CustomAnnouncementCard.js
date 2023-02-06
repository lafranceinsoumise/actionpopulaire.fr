import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledAnnouncement = styled.div`
  width: 100%;
  display: flex;
  padding: 1.5rem 2rem;
  flex-flow: row nowrap;
  align-items: flex-start;
  justify-content: space-between;
  background-color: ${style.secondary100};
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5em;
  }

  & > * {
    flex: 0 0 auto;
  }

  & > div {
    width: 80px;
    height: 80px;
    background-repeat: no-repeat;
    background-size: contain;
    background-position: top center;

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  & > article {
    flex: 1 1 auto;
    margin: 0;
    padding: 0;
    padding-right: 1.5rem;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;

    & > * {
      display: block;
      margin: 0;
      line-height: 1.6;
    }

    span {
      font-weight: 400;
    }

    strong {
      font-weight: 600;
    }

    a {
      text-decoration: underline;
    }
  }

  & > div + article {
    padding-left: 1.5rem;

    @media (max-width: ${style.collapse}px) {
      padding-left: 0;
    }
  }

  & > button {
    display: inline-flex;
    background-color: transparent;
    border: none;
    outline: none;
    cursor: pointer;
    padding: 0;
    margin: 0;
  }
`;

export const CustomAnnouncementCard = (props) => {
  const {
    config,
    illustration,
    title,
    children,
    onClose,
    useAnnouncementData,
  } = props;

  if (!children && useAnnouncementData) {
    return (
      <StyledAnnouncement>
        <article>
          <strong>{title || config.title}</strong>
          <div dangerouslySetInnerHTML={{ __html: config.content }} />
        </article>
        <button onClick={onClose} aria-label="Fermer ce message">
          <RawFeatherIcon name="x" color={style.black1000} />
        </button>
      </StyledAnnouncement>
    );
  }

  if (typeof children === "function") {
    return (
      <StyledAnnouncement>
        {children(config, onClose)}
        <button onClick={onClose} aria-label="Fermer ce message">
          <RawFeatherIcon name="x" color={style.black1000} />
        </button>
      </StyledAnnouncement>
    );
  }

  return (
    <StyledAnnouncement>
      {illustration && (
        <div
          aria-hidden="true"
          style={{ backgroundImage: `url(${illustration})` }}
        />
      )}
      <article>
        {title && <strong>{title}</strong>}
        {children}
      </article>
      <button onClick={onClose} aria-label="Fermer ce message">
        <RawFeatherIcon name="x" color={style.black1000} />
      </button>
    </StyledAnnouncement>
  );
};

const HookedCustomAnnouncementCard = ({ slug, ...rest }) => {
  const [customAnnouncement, onClose] = useCustomAnnouncement(slug);
  const [shouldShow, setShouldShow] = useState(!!customAnnouncement);

  const close = useCallback(() => {
    setShouldShow(false);
    onClose && onClose();
  }, [onClose]);

  useEffect(() => {
    setShouldShow(!!customAnnouncement);
  }, [customAnnouncement]);

  return shouldShow ? (
    <CustomAnnouncementCard
      {...rest}
      config={customAnnouncement}
      onClose={close}
    />
  ) : null;
};

CustomAnnouncementCard.propTypes = {
  illustration: PropTypes.string,
  title: PropTypes.string,
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.func]),
  onClose: PropTypes.func,
  config: PropTypes.object,
  useAnnouncementData: PropTypes.bool,
};
HookedCustomAnnouncementCard.propTypes = {
  illustration: PropTypes.string,
  title: PropTypes.string,
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.func]),
  slug: PropTypes.string.isRequired,
};

export default HookedCustomAnnouncementCard;
