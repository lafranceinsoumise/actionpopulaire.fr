import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";

import Modal from "@agir/front/genericComponents/Modal";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import promo1 from "./promo-message1.svg";
import promo2 from "./promo-message2.svg";
import promo3 from "./promo-message3.svg";
import promo4 from "./promo-message4.svg";

const CloseButton = styled.button``;

const StyledModalContent = styled.div`
  position: relative;
  text-align: center;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  padding: 0 0 36px;
  margin: 60px auto 0;
  box-shadow: ${(props) => props.theme.elaborateShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.background0};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin-top: 20px;
    max-width: calc(100% - 40px);
    padding: 0 0 1.5rem;
  }

  & > * {
    margin: 0;
    padding: 0 3.375rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 0 1.5rem;
    }
  }

  ${CloseButton} {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0;
    color: ${(props) => props.theme.text1000};
    z-index: 1;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  header {
    position: relative;
    width: 100%;
    height: 177px;
    background-color: ${(props) => props.theme.secondary500};
    background-position: bottom center;
    background-repeat: no-repeat;
    margin-bottom: 56px;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 100px;
      background-size: 160px auto;
    }

    &::after {
      content: "";
      display: block;
      background-color: transparent;
      background-repeat: no-repeat;
      background-size: cover;
      width: 100px;
      height: 100px;
      position: absolute;
      bottom: 0;
      left: 50%;
      transform: translate3d(-50%, 50%, 0);
    }
  }
`;

const Container = styled.div`
  display: inline-flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;
  width: 100%;
  border: 1px solid #dfdfdf;
  background-color: ${(props) => props.theme.background0};

  & > div:nth-child(2) {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;

    img {
      display: inline-block;
      background-color: ${(props) => props.theme.white};
      border-radius: 2rem;
      padding: 1rem;
      user-select: none;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        width: 150px;
      }
    }
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1rem;
  }
`;

const Title = styled.div`
  margin: 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 1rem;
    text-align: center;
  }
`;

const Arrow = styled.div`
  border: 1px solid #dfdfdf;
  border-radius: 100px;
  display: inline-flex;
  padding: 0.5rem;
  cursor: pointer;
  user-select: none;
`;

const Mark = styled.span`
  width: 0.5rem;
  height: 0.5rem;
  margin: 0.188rem;
  display: inline-block;
  border-radius: 2rem;
  cursor: pointer;
  transition: background-color 0.5s ease-in-out;
  background-color: ${(props) =>
    props.$active ? props.theme.text700 : props.theme.text200};
`;

const StyledContent = styled.div`
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100px;

  p {
    text-align: center;
    max-width: 600px;
    font-size: 18px;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 14px;
    }
  }
`;

const items = [
  {
    img: promo1,
    content: (
      <p>
        <strong>
          Lancez une première conversation dans votre groupe&nbsp;!{" "}
        </strong>
        Discustez de vos prochaines actions sur Action Populaire
      </p>
    ),
  },
  {
    img: promo2,
    content: (
      <p>
        <strong>Joignez simplement vos membres&nbsp;: </strong>
        tous vos membres recevront un e-mail avec le contenu de votre message et
        pourront y répondre sur le site
      </p>
    ),
  },
  {
    img: promo3,
    content: (
      <p>
        <strong>Organisez ensemble vos actions&nbsp;: </strong>
        les membres du groupe sont les seuls à voir et commenter
      </p>
    ),
  },
  {
    img: promo4,
    content: (
      <p>
        <strong>Restez connecté·es&nbsp;! </strong>
        Recevez les notifications de message en téléchargeant l’application
      </p>
    ),
  },
];

export const PromoMessage = (props) => {
  const { onClick, onClose, goToMessages } = props;

  const [itemIndex, setItemIndex] = useState(0);

  const handleNext = () => {
    setItemIndex((itemIndex + 1) % items.length);
  };
  const handlePrev = () => {
    setItemIndex((itemIndex + items.length - 1) % items.length);
  };
  const handleClick = () => {
    onClick();
    !!onClose && onClose();
  };

  return (
    <Container>
      <Title>La messagerie de votre groupe</Title>
      <div>
        <Arrow>
          <RawFeatherIcon
            name="chevron-left"
            width="1.5rem"
            height="1.5rem"
            onClick={handlePrev}
          />
        </Arrow>
        <img src={items[itemIndex].img} width="280" height="192" />
        <Arrow>
          <RawFeatherIcon
            name="chevron-right"
            width="1.5rem"
            height="1.5rem"
            onClick={handleNext}
          />
        </Arrow>
      </div>

      <div style={{ marginTop: "1rem" }}>
        {items.map((_, i) => (
          <Mark
            key={i}
            $active={i === itemIndex}
            onClick={() => setItemIndex(i)}
          />
        ))}
      </div>

      <StyledContent>{items[itemIndex].content}</StyledContent>

      <Button color="confirmed" onClick={handleClick} wrap icon="edit">
        {goToMessages ? "Voir l'onglet messages" : "Nouveau message de groupe"}
      </Button>
    </Container>
  );
};

export const PromoMessageModal = (props) => {
  const { shouldShow = false, onClose } = props;
  return (
    <Modal shouldShow={shouldShow} onClose={onClose}>
      <StyledModalContent>
        <CloseButton onClick={onClose} aria-label="Fermer la modale">
          <RawFeatherIcon name="x" width="2rem" height="2rem" />
        </CloseButton>
        <PromoMessage {...props} />
      </StyledModalContent>
    </Modal>
  );
};

PromoMessageModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  onClick: PropTypes.func,
};

export default PromoMessageModal;
