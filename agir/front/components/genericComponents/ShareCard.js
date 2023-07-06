import PropTypes from "prop-types";
import React, { useCallback, useRef, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";

import facebookLogo from "@agir/front/genericComponents/logos/facebook.svg";
import telegramLogo from "@agir/front/genericComponents/logos/telegram.svg";
import twitterLogo from "@agir/front/genericComponents/logos/twitter.svg";
import whatsappLogo from "@agir/front/genericComponents/logos/whatsapp.svg";

import { relativeToAbsoluteURL } from "@agir/lib/utils/url";

const StyledCard = styled(Card)`
  margin-bottom: 1.5rem;
  overflow: hidden;
  border-bottom: 1px solid ${(props) => props.theme.black50};
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: center;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    flex-flow: column nowrap;
    align-items: stretch;
  }

  & > * {
    margin: 0;
  }

  nav {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      justify-content: flex-start;
      gap: 1rem;
    }

    a {
      flex: 0 0 auto;
      margin: 0;
      padding: 0;
      font-size: 0;
      line-height: 0;

      img {
        display: inline-block;
        width: auto;
        height: auto;
        max-width: 1.5rem;
        max-height: 1.5rem;
      }
    }
  }

  input {
    width: 100%;
    height: 32px;
    border: 1px solid ${(props) => props.theme.black100};
    border-radius: ${(props) => props.theme.borderRadius}px;
    padding: 8px;
  }

  ${Button} {
    align-self: flex-start;
  }
`;

const ShareCard = (props) => {
  const { url, title, ...rest } = props;

  const absoluteURL = url ? relativeToAbsoluteURL(url) : window.location.href;
  const encodedLocation = encodeURIComponent(absoluteURL);

  let [copied, setCopied] = useState(false);
  let copyUrl = useCallback(() => {
    inputEl.current.select();
    document.execCommand("copy");
    setCopied(true);
  }, []);

  const inputEl = useRef(null);
  return (
    <StyledCard style={{ padding: "1.5rem" }} {...rest}>
      <h4>{title || "Partager"}</h4>
      <nav>
        <a
          href={`https://wa.me/?text=${encodedLocation}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src={whatsappLogo} width="24" height="25" alt="Whatsapp" />
        </a>
        <a
          href={`https://t.me/share/url?url=${encodedLocation}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src={telegramLogo} width="24" height="24" alt="Telegram" />
        </a>
        <a
          href={`https://www.facebook.com/sharer/sharer.php?u=${encodedLocation}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src={facebookLogo} width="24" height="24" alt="Facebook" />
        </a>
        <a
          href={`https://twitter.com/intent/tweet?text=${encodedLocation}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src={twitterLogo} width="24" height="20" alt="Twitter" />
        </a>
      </nav>
      <input
        type="text"
        value={absoluteURL}
        readOnly
        ref={inputEl}
        onClick={copyUrl}
      />
      <Button small icon={copied ? "check" : "copy"} onClick={copyUrl}>
        Copier le lien
      </Button>
    </StyledCard>
  );
};
ShareCard.propTypes = {
  title: PropTypes.string,
  url: PropTypes.string,
};
export default ShareCard;
