import React, { useCallback, useRef, useState } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import nonReactRoutes from "@agir/front/globalContext/nonReactRoutes.config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";
import { routeConfig } from "@agir/front/app/routes.config";

const searchRoute = nonReactRoutes.search;

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
    padding-left: 0.75rem;
    padding-right: 0.5rem;
    align-self: center;
    display: flex;

    svg {
      stroke: ${({ $focused, $empty }) =>
        $focused || !$empty ? style.black1000 : style.black500};
    }
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
    border-radius: ${style.softBorderRadius};
  }

  ${SearchBarInput}::placeholder {
    color: ${style.black500};
    font-weight: 400;
    text-overflow: ellipsis;
    font-size: 0.875rem;
    opacity: 1;
  }

  ${SearchBarButton} {
    padding: 0;
    margin: 0.25rem;
    width: 2rem;
    height: 2rem;
    display: ${({ $focused, $empty }) =>
      $focused || !$empty ? "flex" : "none"};
  }
`;

const SearchBar = () => {
  const inputRef = useRef();
  const location = window.location;

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

  if (location.pathname.includes(routeConfig.search.path)) {
    return null;
  }

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
          strokeWidth={1.33}
        />
      </SearchBarIndicator>

      <SearchBarInput
        ref={inputRef}
        required
        placeholder="Rechercher un groupe ou une action"
        type="text"
        name="q"
        onFocus={handleFocus}
        onBlur={handleBlur}
        onChange={handleChange}
        value={value.slice(0, 512)}
        maxLength="512"
      />
      <SearchBarButton type="submit" color="primary">
        <RawFeatherIcon
          name="arrow-right"
          color="#fff"
          width="1rem"
          height="1rem"
          strokeWidth={2}
        />
      </SearchBarButton>
    </SearchBarWrapper>
  );
};

export default SearchBar;
