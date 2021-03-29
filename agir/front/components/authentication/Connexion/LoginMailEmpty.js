import React, { useState, useCallback } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import Link from "@agir/front/app/Link";
import { login } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory, useLocation } from "react-router-dom";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const Form = styled.form`
  box-sizing: border-box;
  margin: 0 auto;
  margin-top: 2rem;
  display: flex;
  text-align: left;

  Button {
    margin-top: 1.5rem;
    margin-left: 0.625rem;
    width: 140px;
    height: 41px;
    justify-content: center;
  }

  & > :first-child {
    width: 100%;
  }

  @media (max-width: ${style.collapse}px) {
    flex-flow: wrap;
    & > :first-child {
      max-width: 100%;
      width: 100%;
    }
    div {
      width: 100%;
      Button {
        width: 100%;
        margin-left: 0;
        margin-top: 0.875rem;
      }
    }
  }
`;

const LoginMailEmpty = () => {
  const history = useHistory();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [error, setError] = useState({});

  let next = "";
  if (location.search !== undefined)
    next = new URLSearchParams(location.search).get("next");

  const handleInputChange = useCallback((e) => {
    setEmail(e.target.value);
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setError({});
      const result = await login(email);
      if (result.error) {
        setError(result.error);
        return;
      }
      const route = routeConfig.codeLogin.getLink();
      history.push(route, {
        email: email,
        code: result.data && result.data.code,
        next: next,
      });
    },
    [history, email]
  );

  return (
    <Form onSubmit={handleSubmit}>
      <div>
        <TextField
          id="email"
          label="Adresse e-mail"
          error={error && (error.email || error.detail)}
          placeholder="Adresse e-mail"
          onChange={handleInputChange}
          value={email}
          name="email"
          autoComplete="email"
        />
        {!!error.detail && (
          <Link route="codeLogin">
            Accéder à la page pour demander son code
          </Link>
        )}
      </div>
      <div>
        <Button color="primary" type="submit">
          Me connecter
        </Button>
      </div>
    </Form>
  );
};

export default LoginMailEmpty;
