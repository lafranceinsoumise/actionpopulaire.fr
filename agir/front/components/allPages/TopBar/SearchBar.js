import React, { useCallback, useRef, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const SearchBarIndicator = styled.div``;
const SearchBarButton = styled(Button)``;

const SearchBarInput = styled.input``;

const SearchBarWrapper = styled.div`
  max-width: ${({ $connected }) => ($connected ? "353px" : "412px")};
  display: flex;
  border: 1px solid;
  border-color: ${({ $focused }) =>
    $focused ? style.black1000 : style.black100};
  border-radius: 8px;
  align-items: center;
  height: 40px;

  ${SearchBarIndicator} {
    padding: 0;
    padding-left: 18px;
    padding-right: 0.5rem;
  }

  ${SearchBarButton} {
    margin: 4px;
    padding: revert;
    width: 2rem;
    height: 2rem;
    opacity: ${({ $focused }) => ($focused ? 1 : 0)};
    transition: 0.1s ease;
  }

  ${SearchBarIndicator} {
    align-self: center;
    display: flex;
  }

  ${SearchBarInput} {
    width: 100%;
    height: 2rem;
    margin: 0;
    padding: 0;
    color: ${style.black1000};
    border: none;
    background-color: transparent;
    outline: none;

    &::placeholder {
      color: ${style.black500};
      font-weight: 500;
      opacity: 1;
    }
  }
`;

const SearchBar = ({ isConnected = false }) => {
  const inputRef = useRef();
  const [isFocused, setIsFocused] = useState(false);
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);
  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);
  const handleClick = useCallback((e) => {
    if (inputRef.current.value.trim() === "") {
      inputRef.current.focus();
      e.preventDefault();
    }
  }, []);
  return (
    <SearchBarWrapper $focused={isFocused} $connected={isConnected}>
      <SearchBarIndicator>
        <RawFeatherIcon
          name="search"
          color={style.black1000}
          width="1rem"
          height="1rem"
          stroke-width={1.33}
        />
      </SearchBarIndicator>

      <SearchBarInput
        ref={inputRef}
        placeholder={
          !isConnected
            ? "Rechercher un groupe ou une action"
            : "Rechercher sur Action Populaire"
        }
        type="text"
        name="q"
        onFocus={handleFocus}
        onBlur={handleBlur}
      />
      <SearchBarButton onClick={handleClick} type="submit" color="primary">
        <RawFeatherIcon
          name="arrow-right"
          color="#fff"
          width="1rem"
          height="1rem"
          stroke-width={2}
        />
      </SearchBarButton>
    </SearchBarWrapper>
  );
};

export default SearchBar;
