import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { MailTo } from "@agir/elections/Common/StyledComponents";

import votingProxyRequestIcon from "@agir/voting_proxies/Common/images/vpr_icon.svg";
import votingProxyIcon from "@agir/voting_proxies/Common/images/vp_icon.svg";

const StyledFooterLink = styled.div`
  display: flex;
  align-items: center;
  padding: 1.5rem;
  font-size: 0.875rem;
  gap: 0.5rem;

  & > p {
    flex: 1 1 auto;

    ${Button} {
      font-weight: 600;
      text-align: left;
    }
  }

  & > img {
    flex: 0 0 auto;
  }
`;

const FormFooter = ({ votingProxyLink, votingProxyRequestLink }) => {
  return (
    <>
      <MailTo />
      {votingProxyRequestLink && (
        <StyledFooterLink>
          <p>
            Vous ne vous pouvez pas vous déplacer les jours de scrutin&nbsp;?{" "}
            <br />
            <Button
              small
              link
              wrap
              color="link"
              icon="arrow-right"
              route="newVotingProxyRequest"
            >
              Permettez à quelqu'un de voter à votre place
            </Button>
          </p>
          <img src={votingProxyRequestIcon} width="88" height="81" />
        </StyledFooterLink>
      )}
      {votingProxyLink && (
        <StyledFooterLink>
          <p>
            Disponible un jour de vote&nbsp;?
            <br />
            <Button
              small
              link
              wrap
              color="link"
              icon="arrow-right"
              route="newVotingProxy"
            >
              Je suis volontaire pour prendre une procuration
            </Button>
          </p>
          <img src={votingProxyIcon} width="88" height="81" />
        </StyledFooterLink>
      )}
    </>
  );
};

FormFooter.propTypes = {
  votingProxyLink: PropTypes.bool,
  votingProxyRequestLink: PropTypes.bool,
};

export default FormFooter;
