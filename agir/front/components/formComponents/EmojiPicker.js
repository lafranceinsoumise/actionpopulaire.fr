import { Emoji, Picker } from "emoji-mart";
import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import { animated, useTransition } from "react-spring";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import style from "@agir/front/genericComponents/_variables.scss";

import "emoji-mart/css/emoji-mart.css";

const i18n = {
  search: "Recherche",
  clear: "Réinitialiser la recherche", // Accessible label on "clear" button
  notfound: "Aucun emoji ne correspond à la recherche",
  skintext: "Choisissez une couleur de peau par défaut",
  categories: {
    search: "Résultats",
    recent: " ",
    smileys: "Émoticones",
    people: "Personnes",
    nature: "Nature",
    foods: "Nourriture",
    activity: "Activités",
    places: "Voyage",
    objects: "Objets",
    symbols: "Symboles",
    flags: "Drapeaux",
    custom: "Personnalisés",
  },
  categorieslabel: "Catégories d'emojis", // Accessible title for the list of categories
  skintones: {
    1: "Couleur de peau par défaut",
    2: "Couleur de peau très claire",
    3: "Couleur de peau claire",
    4: "Couleur de peau moyenne",
    5: "Couleur de peau sombre",
    6: "Couleur de peau très sombre",
  },
};

const StyledOverlay = styled.div`
  display: ${({ $isOpen }) => ($isOpen ? "block" : "none")};
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: transparent;
  cursor: pointer;
  z-index: 0;
`;
const StyledTriggerIcon = styled(animated.span)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: ${({ $size }) => $size || 24}px;
  width: ${({ $size }) => $size || 24}px;
  margin: 0;
  padding: 0;
  position: relative;

  & > * {
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    line-height: 1.5;
    transform-origin: center center;
    transition: opacity, transform 100ms ease-in-out;
  }

  & > :first-child {
    opacity: ${({ $isOpen }) => (!$isOpen ? 1 : 0)};
    transform: ${({ $isOpen }) => (!$isOpen ? "scale(1,1)" : "scale(0.5,0.5)")};
  }

  & > :last-child {
    opacity: ${({ $isOpen }) => ($isOpen ? 1 : 0)};
    transform: ${({ $isOpen }) => ($isOpen ? "scale(1,1)" : "scale(0.5,0.5)")};
  }
`;
const StyledTrigger = styled.button`
  display: inline-block;
  border: none;
  padding: 0;
  margin: 0;
  text-decoration: none;
  background: inherit;
  color: inherit;
  font-size: 0;
  line-height: 0;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;

  &:hover,
  &:focus {
    border: none;
    outline: none;
    opacity: 0.6;
  }
`;
const StyledPickerWrapper = styled(animated.div)`
  position: absolute;
  width: 350px;
  right: 0;
  top: 100%;
  text-align: left;
  z-index: 1;

  @media (max-width: ${style.collapse}px) {
    position: fixed;
    top: unset;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 1;
  }
`;

const StyledWrapper = styled.div`
  position: relative;
  display: inline-block;
  line-height: 1;
`;

const slideInTransition = {
  from: { opacity: 0, transform: "translateY(1rem)" },
  enter: { opacity: 1, transform: "translateY(0)" },
  leave: { opacity: 0, transform: "translateY(1rem)" },
};

const EmojiPicker = (props) => {
  const { onSelect, format, small } = props;
  const [isOpen, setIsOpen] = useState(false);

  const toggleOpen = useCallback(() => {
    setIsOpen((state) => !state);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  const handleKeyClose = useCallback((e) => {
    e.key === "Escape" && setIsOpen(false);
  }, []);

  const handleSelect = useCallback(
    (emoji) => {
      onSelect(emoji[format] || emoji.native);
    },
    [onSelect, format]
  );

  const transition = useTransition(isOpen, null, slideInTransition);

  React.useEffect(() => {
    isOpen && document.addEventListener("keydown", handleKeyClose);
    return () => document.removeEventListener("keydown", handleKeyClose);
  }, [isOpen, handleKeyClose]);

  return (
    <>
      <StyledOverlay onClick={handleClose} $isOpen={isOpen} />
      <StyledWrapper>
        <StyledTrigger type="button" onClick={toggleOpen}>
          <StyledTriggerIcon $isOpen={isOpen} $size={small ? "1rem" : "1.5rem"}>
            <RawFeatherIcon
              name="smile"
              width={small ? "1rem" : "1.5rem"}
              color={style.black1000}
            />
            <Emoji
              emoji="smile"
              size={small ? "1rem" : "1.5rem"}
              set="twitter"
            />
          </StyledTriggerIcon>
        </StyledTrigger>
        {transition.map(
          ({ item, key, props }) =>
            item && (
              <StyledPickerWrapper key={key} style={props}>
                <Picker
                  autoFocus
                  showPreview={false}
                  showSkinTones={false}
                  onSelect={handleSelect}
                  onKeyDown={handleKeyClose}
                  title=""
                  style={{
                    width: "100%",
                    fontFamily: "inherit",
                    fontSize: "14px",
                    lineHeight: "1.5",
                  }}
                  i18n={i18n}
                  color={style.primary500}
                  set="twitter"
                />
              </StyledPickerWrapper>
            )
        )}
      </StyledWrapper>
    </>
  );
};
EmojiPicker.propTypes = {
  onSelect: PropTypes.func.isRequired,
  format: PropTypes.oneOf(["native", "id", "colons", "unified"]),
  small: PropTypes.bool,
};
EmojiPicker.defaultProps = {
  format: "native",
  small: false,
};
export default EmojiPicker;
