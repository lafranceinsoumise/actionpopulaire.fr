import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import Modal from "@agir/front/genericComponents/Modal";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import style from "@agir/front/genericComponents/_variables.scss";
import { FaWhatsapp, FaFacebook } from "react-icons/fa";

const StyledWrapper = styled.div`
  display: flex;
  width: 100%;
  flex-flow: column nowrap;
  gap: 0.5rem;

  ${Button} {
    ${"" /* TODO: remove after Button refactoring merge */}
    width: 100%;
    margin: 0;
    justify-content: center;
  }

  p {
    margin: 0.5rem 0 0;
    text-align: center;
    font-size: 0.688rem;
    font-weight: 400;
    line-height: 1.5;
    color: ${(props) => props.theme.black700};
  }
`;

const StyledContainer = styled.div`
  display: flex;
  flex-align: row;
  justify-content: center;

  ${Button} {
    background-color: white;
    font-size: 12px;
    border: none;
    display: inline-flex;
    flex-direction: column;
    width: inherit;
  }
`;

const ModalContainer = styled.div`
  background: white;
  height: 60%;
  width: 40%;
  margin: 5% auto;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border-radius: s ${style.borderRadius};

  @media (max-width: ${style.collapse}px) {
    width: 90%;
    height: 90%;
  }
`;

const ModalContent = styled.div`
  display: inline-flex;
  flex-direction: column;
  padding: 1rem;

  h1 {
    font-size: 1rem;
  }

  > ${Button} {
    margin-bottom: 1rem;
    color: white;
  }
`;

const NonMemberActions = (props) => {
  const { onJoin, onFollow, isLoading, routes } = props;

  const [isOpen, setIsOpen] = useState(false);

  const url = encodeURIComponent(routes.details);

  const handleClose = () => setIsOpen(false);
  const handleShare = () => setIsOpen(true);

  return (
    <StyledWrapper>
      <Button
        type="button"
        color="success"
        disabled={isLoading}
        onClick={onJoin}
      >
        <RawFeatherIcon name="user-plus" width="1.5rem" height="1.5rem" />
        <Spacer size="10px" />
        Rejoindre
      </Button>
      <Button type="button" disabled={isLoading} onClick={onFollow}>
        <RawFeatherIcon name="plus" width="1.5rem" height="1.5rem" />
        <Spacer size="10px" />
        Suivre
      </Button>

      <StyledContainer>
        <Button type="button">
          <RawFeatherIcon name="mail" width="1rem" height="1rem" />
          Contacter
        </Button>
        {!!routes?.donations && (
          <Button type="button" link route={routes.donations}>
            <RawFeatherIcon name="upload" width="1rem" height="1rem" />
            Financer
          </Button>
        )}
        <Button type="button" onClick={handleShare}>
          <RawFeatherIcon name="share-2" width="1rem" height="1rem" />
          Partager
        </Button>
      </StyledContainer>

      <Modal shouldShow={isOpen} onClose={handleClose}>
        <ModalContainer>
          <ModalContent>
            <h1>Partager la page</h1>

            <Button
              style={{ backgroundColor: style.facebook }}
              type="button"
              link
              target="_blank"
              rel="noopener noreferrer"
              href={`https://www.facebook.com/sharer/sharer.php?u=${url}`}
            >
              <FaFacebook
                size="1.5rem"
                height="32"
                width="32"
                color={style.white}
              />
              &nbsp; Partager sur Facebook
            </Button>
            <Button
              style={{ backgroundColor: style.twitter }}
              type="button"
              link
              target="_blank"
              rel="noopener noreferrer"
              href={`https://twitter.com/intent/tweet?text=${url}`}
            >
              <RawFeatherIcon name="twitter" width="1.5rem" height="1.5rem" />
              &nbsp; Partager sur Twitter
            </Button>
            <Button
              style={{ backgroundColor: style.whatsapp }}
              type="button"
              link
              target="_blank"
              rel="noopener noreferrer"
              href={`https://wa.me/?text=${url}`}
            >
              <FaWhatsapp
                size="1.5rem"
                height="32"
                width="32"
                color={style.white}
              />
              &nbsp; Partager sur Whatsapp
            </Button>
            <ShareLink label="Copier le lien" url={routes.details} />
          </ModalContent>
        </ModalContainer>
      </Modal>
    </StyledWrapper>
  );
};
NonMemberActions.propTypes = {
  onJoin: PropTypes.func,
  onFollow: PropTypes.func,
  isLoading: PropTypes.bool,
};
export default NonMemberActions;
