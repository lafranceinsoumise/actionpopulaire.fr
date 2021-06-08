import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import Link from "@agir/front/app/Link";
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

const LoginMailEmpty = ({ onSubmit, error }) => {
  const [email, setEmail] = useState("");

  const handleInputChange = useCallback((e) => {
    setEmail(e.target.value);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(email);
  };

  return (
    <Form onSubmit={handleSubmit}>
      <div>
        <TextField
          id="email"
          label="Adresse e-mail"
          error={error?.email || error?.detail}
          placeholder="Adresse e-mail"
          onChange={handleInputChange}
          value={email}
          name="email"
          autoComplete="email"
          type="email"
        />
        {error?.detail && (
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

LoginMailEmpty.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  error: PropTypes.shape({
    email: PropTypes.string,
    detail: PropTypes.string,
  }),
};
export default LoginMailEmpty;
