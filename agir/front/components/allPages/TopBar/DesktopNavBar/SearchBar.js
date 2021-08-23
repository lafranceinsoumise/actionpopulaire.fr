import PropTypes from "prop-types";
import React, { useCallback, useRef, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { search as searchRoute } from "@agir/front/globalContext/nonReactRoutes.config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const SearchBarIndicator = styled.div``;
const SearchBarButton = styled(Button)``;
const SearchBarInput = styled.input``;
const SearchBarWrapper = styled.form`
  display: flex;
  border: 1px solid;
  border-color: ${({ $focused, $empty }) =>
    $focused || !$empty ? style.black1000 : style.black100};
  border-radius: ${style.borderRadius};
  align-items: center;
  height: 40px;

  ${SearchBarIndicator} {
    padding: 0;
    padding-left: 18px;
    padding-right: 0.5rem;
    align-self: center;
    display: flex;

    svg {
      stroke: ${({ $focused, $empty }) =>
        $focused || !$empty ? style.black1000 : style.black500};
    }
  }

  ${SearchBarButton} {
    margin: 4px;
    padding: revert;
    width: 2rem;
    height: 2rem;
    opacity: ${({ $focused, $empty }) => ($focused || !$empty ? 1 : 0)};
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
    border-radius: ${style.softBorderRadius}

    &::placeholder {
      color: ${style.black500};
      font-weight: 500;
      opacity: 1;
      max-width: 100%;
      text-overflow: ellipsis;
    }
  }
`;

const SearchBar = ({ isConnected }) => {
  const inputRef = useRef();
  const [value, setValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);
  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);
  const handleChange = (e) => setValue(e.target.value);
  const handleSubmit = useCallback((e) => {
    if (inputRef.current.value.trim() === "") {
      e.preventDefault();
      inputRef.current.focus();
    }
  }, []);
  return (
    <SearchBarWrapper
      method="get"
      action={searchRoute}
      onSubmit={handleSubmit}
      $focused={isFocused}
      $empty={value === ""}
    >
      <SearchBarIndicator>
        <RawFeatherIcon
          name="search"
          width="1rem"
          height="1rem"
          stroke-width={1.33}
        />
      </SearchBarIndicator>

      <SearchBarInput
        ref={inputRef}
        required
        placeholder={
          isConnected
            ? "Rechercher sur Action Populaire"
            : "Rechercher un groupe ou une action"
        }
        type="text"
        name="q"
        onFocus={handleFocus}
        onBlur={handleBlur}
        onChange={handleChange}
        value={value}
      />
      <SearchBarButton type="submit" color="primary">
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

SearchBar.propTypes = {
  isConnected: PropTypes.bool,
};
export default SearchBar;
