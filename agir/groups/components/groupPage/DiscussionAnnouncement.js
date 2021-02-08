import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import illustration from "@agir/groups/groupPage/images/empty-messages-bg.svg";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledAnnouncement = styled.div`
  width: 100%;
  display: flex;
  padding: 1.75rem 1rem;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: space-between;
  background-color: ${style.secondary100};
  position: relative;

  & > * {
    flex: 0 0 auto;
  }

  div {
    width: 102px;
    height: 98px;
    background-image: url(${illustration});
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center left;
  }

  p {
    flex: 1 1 auto;
    margin: 0 0 0 1.5rem;
    display: flex;
    flex-flow: column nowrap;

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
  }

  button {
    display: inline-flex;
    background-color: transparent;
    border: none;
    outline: none;
    cursor: pointer;
    padding: 0;
    margin: 0;
    position: absolute;
    top: 0.875rem;
    right: 1rem;
  }
`;

const DiscussionAnnouncement = ({ isActive, onClose }) => {
  const [shouldShow, setShouldShow] = useState(isActive);

  const close = useCallback(() => {
    setShouldShow(false);
    onClose && onClose();
  }, [onClose]);

  return shouldShow ? (
    <StyledAnnouncement>
      <div aria-hidden="true" />
      <p>
        <br />
        <strong>
          Nouveau&nbsp;: discutez de vos prochaines actions ici&nbsp;!
        </strong>
        <br />
        <span>
          Vos animateur·ices publieront des messages auxquels vous pourrez
          répondre sur cette page.
        </span>
      </p>
      <button onClick={close} aria-label="Fermer ce message">
        <RawFeatherIcon name="x" color={style.black1000} />
      </button>
    </StyledAnnouncement>
  ) : null;
};
DiscussionAnnouncement.propTypes = {
  isActive: PropTypes.bool,
  onClose: PropTypes.func,
};
export default DiscussionAnnouncement;
