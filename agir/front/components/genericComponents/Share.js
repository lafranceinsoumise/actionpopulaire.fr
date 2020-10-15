import Card from "./Card";
import React from "react";
import Button from "./Button";
import { Column, Row } from "./grid";
import facebookLogo from "./logos/facebook.svg";
import twitterLogo from "./logos/twitter.svg";
import telegramLogo from "./logos/telegram.svg";
import whatsappLogo from "./logos/whatsapp.svg";

let logoSpacing = { margin: "0 8px" };

const Share = () => {
  let encodedLocation = encodeURIComponent(window.location.href);
  return (
    <Card>
      <Row gutter={2}>
        <Column fill collapse={false}>
          <p>
            <b>Partager</b>
          </p>
        </Column>
        <Column collapse={false}>
          <a href={`https://wa.me/?text=${encodedLocation}`}>
            <img src={whatsappLogo} style={logoSpacing} alt="Whatsapp" />
          </a>
          <a href={`https://t.me/share/url?url=${encodedLocation}`}>
            <img src={telegramLogo} style={logoSpacing} alt="Telegram" />
          </a>
          <a
            href={`https://www.facebook.com/sharer/sharer.php?u=${encodedLocation}`}
          >
            <img src={facebookLogo} style={logoSpacing} alt="Facebook" />
          </a>
          <a href={`https://twitter.com/intent/tweet?text=${encodedLocation}`}>
            <img
              src={twitterLogo}
              style={{ ...logoSpacing, marginRight: 0 }}
              alt="Twitter"
            />
          </a>
        </Column>
      </Row>

      <Row gutter={4}>
        <Column fill collapse={false}>
          {" "}
          <input type="text" value="Prout" style={{ width: "100%" }} />
        </Column>
        <Column collapse={false}>
          <Button small icon="copy">
            Copier le lien
          </Button>
        </Column>
      </Row>
    </Card>
  );
};
export default Share;
