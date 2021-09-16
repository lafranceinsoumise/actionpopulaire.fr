import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import Modal from "@agir/front/genericComponents/Modal";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import style from "@agir/front/genericComponents/_variables.scss";
import { FaWhatsapp, FaFacebook, FaTelegramPlane } from "react-icons/fa";

const ModalContainer = styled.div`
  background: white;
  width: 40%;
  width: fit-content;
  margin: 5% auto;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border-radius: ${style.borderRadius};

  @media (max-width: ${style.collapse}px) {
    width: 90%;
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

const ModalShare = (props) => {
  const { shouldShow = false, onClose, url = window.location.href } = props;

  const urlEncoded = encodeURIComponent(url);

  return (
    <Modal shouldShow={shouldShow} onClose={onClose}>
      <ModalContainer>
        <ModalContent>
          <h1>Partager la page</h1>

          <Button
            style={{ backgroundColor: style.facebook }}
            type="button"
            link
            target="_blank"
            rel="noopener noreferrer"
            href={`https://www.facebook.com/sharer/sharer.php?u=${urlEncoded}`}
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
            href={`https://twitter.com/intent/tweet?text=${urlEncoded}`}
          >
            <RawFeatherIcon name="twitter" width="1.5rem" height="1.5rem" />
            &nbsp; Partager sur Twitter
          </Button>
          <Button
            style={{ backgroundColor: style.telegram }}
            type="button"
            link
            target="_blank"
            rel="noopener noreferrer"
            href={`https://t.me/share/url?url=${urlEncoded}`}
          >
            <FaTelegramPlane
              size="1.5rem"
              height="32"
              width="32"
              color={style.white}
            />
            &nbsp; Partager sur Telegram
          </Button>
          <Button
            style={{ backgroundColor: style.whatsapp }}
            type="button"
            link
            target="_blank"
            rel="noopener noreferrer"
            href={`https://wa.me/?text=${urlEncoded}`}
          >
            <FaWhatsapp
              size="1.5rem"
              height="32"
              width="32"
              color={style.white}
            />
            &nbsp; Partager sur Whatsapp
          </Button>
          <ShareLink $wrap label="Copier le lien" url={url} />
        </ModalContent>
      </ModalContainer>
    </Modal>
  );
};

ModalShare.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  url: PropTypes.string,
};

export default ModalShare;
