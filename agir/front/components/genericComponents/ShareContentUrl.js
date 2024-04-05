import PropTypes from "prop-types";
import React from "react";

import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import * as style from "@agir/front/genericComponents/_variables.scss";
import {
  FaWhatsapp,
  FaFacebook,
  FaTelegram,
} from "@agir/front/genericComponents/FaIcon";

const StyledContainer = styled.div`
  display: inline-flex;
  flex-direction: column;

  & > ${Button} {
    margin-bottom: 1rem;
    color: white;
    line-height: 1.5rem;

    & > span {
      display: inline-flex;
    }
  }
`;

const ShareContentUrl = ({ url }) => {
  const urlEncoded = encodeURIComponent(url);

  return (
    <StyledContainer>
      <Button
        style={{ backgroundColor: style.facebook }}
        type="button"
        link
        target="_blank"
        rel="noopener noreferrer"
        href={`https://www.facebook.com/sharer/sharer.php?u=${urlEncoded}`}
      >
        <FaFacebook size="1.5rem" height="32" width="32" color={style.white} />
        &nbsp; Partager sur Facebook
      </Button>
      <Button
        style={{ backgroundColor: style.twitter }}
        type="button"
        link
        target="_blank"
        rel="noopener noreferrer"
        href={`https://twitter.com/intent/tweet?text=${urlEncoded}`}
      >
        <RawFeatherIcon name="twitter" width="1.5rem" height="1.5rem" />
        &nbsp; Partager sur Twitter
      </Button>
      <Button
        style={{ backgroundColor: style.telegram }}
        type="button"
        link
        target="_blank"
        rel="noopener noreferrer"
        href={`https://t.me/share/url?url=${urlEncoded}`}
      >
        <FaTelegram size="1.5rem" height="32" width="32" color={style.white} />
        &nbsp; Partager sur Telegram
      </Button>
      <Button
        style={{ backgroundColor: style.whatsapp }}
        type="button"
        link
        target="_blank"
        rel="noopener noreferrer"
        href={`https://wa.me/?text=${urlEncoded}`}
      >
        <FaWhatsapp size="1.5rem" height="32" width="32" color={style.white} />
        &nbsp; Partager sur Whatsapp
      </Button>
      <ShareLink $wrap label="Copier le lien" url={url} />
    </StyledContainer>
  );
};
ShareContentUrl.propTypes = {
  url: PropTypes.string,
};

export default ShareContentUrl;
