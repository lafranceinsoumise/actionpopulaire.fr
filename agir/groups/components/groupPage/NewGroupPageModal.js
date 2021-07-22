import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

import style from "@agir/front/genericComponents/_variables.scss";
import illustration from "@agir/groups/groupPage/images/new-page-modal.svg";

import Modal from "@agir/front/genericComponents/Modal";
import Button from "@agir/front/genericComponents/Button";

const StyledModalContent = styled.div`
  max-width: 600px;
  min-height: 431px;
  padding: 2rem;
  margin: 100px auto 0;
  background-color: white;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: center;
  text-align: center;
  box-shadow: ${style.elaborateShadow};
  border-radius: ${style.borderRadius};

  @media (max-width: ${style.collapse}px) {
    max-width: 100%;
    margin: 0;
    box-shadow: none;
    border-radius: 0;
  }

  div {
    width: 100%;
    height: 160px;
    margin-bottom: 2rem;
    background-image: url(${illustration});
    background-repeat: no-repeat;
    background-position: center center;
    background-size: contain;
  }

  h3 {
    font-weight: 700;
    font-size: 1.25rem;
    margin: 0 0 0.5rem;
  }

  p {
    margin: 0;
    font-size: 1rem;
    line-height: 1.6;

    a {
      cursor: pointer;

      &[disabled] {
        cursor: default;
        &:hover,
        &:focus {
          text-decoration: none;
        }
      }
    }
  }

  ${Button} {
    margin: 1.25rem auto;
  }
`;

const NewGroupPageModal = ({ isActive, onClose }) => {
  const [shouldShow, setShouldShow] = useState(isActive);
  const routes = useSelector(getRoutes);

  const close = useCallback(() => {
    setShouldShow(false);
    onClose && onClose();
  }, [onClose]);

  useEffect(() => {
    setShouldShow(isActive);
  }, [isActive]);

  return (
    <Modal shouldShow={shouldShow} noScroll>
      <StyledModalContent>
        <div aria-hidden="true" />
        <h3>Votre page de groupe a fait peau neuve&nbsp;!</h3>
        <p>
          La présentation a été améliorée grâce à{" "}
          <a
            disabled={!routes || !routes.feedbackForm}
            href={routes && routes.feedbackForm}
            target="_blank"
            rel="noopener noreferrer"
          >
            vos retours
          </a>
          &nbsp;!
          <br />
          Toutes vos informations ont été conservées.
        </p>
        <Button onClick={close} color="primary">
          Découvrir
        </Button>
      </StyledModalContent>
    </Modal>
  );
};
NewGroupPageModal.propTypes = {
  isActive: PropTypes.bool,
  onClose: PropTypes.func,
};
export default NewGroupPageModal;
