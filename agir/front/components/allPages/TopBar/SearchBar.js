import React, { useCallback, useRef, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const SearchBarIndicator = styled.div``;
const SearchBarButton = styled.button``;
const SearchBarInput = styled.input``;

const SearchBarWrapper = styled.div`
  max-width: 450px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  border: 1px solid;
  border-color: ${({ $focused }) =>
    $focused ? style.black500 : style.black50};
  background-color: ${({ $focused }) =>
    $focused ? style.white : style.black50};
  border-radius: 3px;
  align-items: center;

  ${SearchBarIndicator},
  ${SearchBarButton} {
    height: 1.5rem;
    margin: 0;
    padding: 0 1rem;
  }

  ${SearchBarIndicator} {
    align-self: center;
  }

  ${SearchBarInput} {
    width: 100%;
    height: 3rem;
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

  ${SearchBarButton} {
    border: 0;
    background: none;
  }
`;

const SearchBar = () => {
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
    <SearchBarWrapper $focused={isFocused}>
      <SearchBarIndicator>
        <FeatherIcon name="search" color={style.black500} alignOnText={false} />
      </SearchBarIndicator>

      <SearchBarInput
        ref={inputRef}
        placeholder="Rechercher un groupe ou un événement"
        type="text"
        name="q"
        onFocus={handleFocus}
        onBlur={handleBlur}
      />
      {isFocused && (
        <SearchBarButton onClick={handleClick} type="submit">
          <FeatherIcon
            name="arrow-right"
            color={style.black500}
            alignOnText={false}
          />
        </SearchBarButton>
      )}
    </SearchBarWrapper>
  );
};

export default SearchBar;
