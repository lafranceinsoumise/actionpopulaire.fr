import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { Column, Row } from "@agir/front/genericComponents/grid";
import { useToast } from "@agir/front/globalContext/hooks.js";

import { inviteToGroup } from "@agir/groups/utils/api";

const StyledContainer = styled.div`
  display: flex;
  align-items: center;

  & > :first-child {
    max-width: 300px;
    width: 100%;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-wrap: wrap;
    & > :first-child {
      width: 100%;
    }
  }
`;

const StyledDiv = styled.div`
  font-weight: 500;
`;

const GroupInvitation = (props) => {
  const { title, groupPk } = props;
  const sendToast = useToast();

  const [email, setEmail] = useState("");
  const [errors, setErrors] = useState({});

  const handleChange = useCallback((e) => {
    setEmail(e.target.value);
  }, []);

  const handleInvitation = useCallback(
    async (e) => {
      e.preventDefault();
      setErrors({});
      const res = await inviteToGroup(groupPk, { email });
      if (res.error) {
        setErrors(res.error);
        return;
      }
      sendToast("Invitation envoyée", "SUCCESS", { autoClose: true });
      setEmail("");
    },
    [email, groupPk, sendToast],
  );

  return (
    <StyledDiv>
      <Row gutter={2} style={{ marginBottom: "1rem" }}>
        <Column grow collapse={0}>
          {title}
        </Column>
      </Row>

      <StyledContainer>
        <div style={{ marginRight: "0.5rem" }}>
          <TextField
            type="text"
            value={email}
            placeholder="Adresse e-mail de l’invité·e"
            onChange={handleChange}
            error={errors?.email}
          />
        </div>
        <div>
          <Button color="primary" small onClick={handleInvitation}>
            Envoyer une invitation
          </Button>
        </div>
      </StyledContainer>
    </StyledDiv>
  );
};
GroupInvitation.propTypes = {
  title: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupInvitation;
