import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";

import style from "@agir/front/genericComponents/_variables.scss";
import illustration from "@agir/groups/groupPage/images/display-name-announcement-bg.svg";

import Link from "@agir/front/app/Link";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledAnnouncement = styled.div`
  width: 100%;
  display: flex;
  padding: 1rem 1.75rem;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: space-between;
  background-color: ${style.secondary100};
  position: relative;
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    padding: 1rem;
    padding-right: 3rem;
    margin-bottom: 1rem;
  }

  & > * {
    flex: 0 0 auto;
  }

  div {
    width: 102px;
    height: 112px;
    background-image: url(${illustration});
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center left;
    margin-right: 1.5rem;

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  p {
    flex: 1 1 auto;
    margin: 0;
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

    @media (max-width: ${style.collapse}px) {
      right: 0.875rem;
    }
  }
`;

const DisplayNameAnnouncement = () => {
  const [displayNameAnnouncement, onClose] = useCustomAnnouncement(
    "DisplayNameAnnouncement"
  );

  const [shouldShow, setShouldShow] = useState(!!displayNameAnnouncement);

  const close = useCallback(() => {
    setShouldShow(false);
    onClose && onClose();
  }, [onClose]);

  useEffect(() => {
    setShouldShow(!!displayNameAnnouncement);
  }, [displayNameAnnouncement]);

  return shouldShow ? (
    <StyledAnnouncement>
      <div aria-hidden="true" />
      <p>
        <strong>Nouveau&nbsp;: nom d'affichage et avatar</strong>
        <span>
          Pour que vos camarades puissent vous reconnaitre, prenez le temps de{" "}
          <Link route="personalInformation">
            modifier ces informations dans votre profil
          </Link>
          .
        </span>
      </p>
      <button onClick={close} aria-label="Fermer ce message">
        <RawFeatherIcon name="x" color={style.black1000} />
      </button>
    </StyledAnnouncement>
  ) : null;
};
export default DisplayNameAnnouncement;
