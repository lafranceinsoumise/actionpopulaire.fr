import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import LogoAP from "@agir/front/genericComponents/LogoAP";

import notificationIllustration from "@agir/front/genericComponents/images/notification-illustration.svg";

const StyledWrapper = styled.div`
  width: 100%;
  max-width: 420px;
  padding: 3.25rem 1.5rem;
  margin: 0 auto;
  text-align: center;

  & > * {
    margin: 0;
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    padding-bottom: 0.5rem;
    text-align: left;
  }

  p {
    text-align: left;
  }

  img {
    margin: 1rem auto;
    height: 162px;
    width: auto;
  }

  ${Button} {
    width: 100%;
    margin-bottom: 1rem;
  }
`;

const DeviceNotificationSubscription = (props) => {
  const { onSubscribe, onDismiss, subscriptionError } = props;
  return (
    <>
      <Hide style={{ position: "fixed" }} under>
        <Link route="events">
          <LogoAP
            style={{ marginTop: "2rem", paddingLeft: "2rem", width: "200px" }}
          />
        </Link>
      </Hide>

      <StyledWrapper>
        <h2>Activer les notifications</h2>
        <p>
          Ne ratez pas les actions près de chez vous et recevez les annonces de
          la campagne.
        </p>
        <img
          src={notificationIllustration}
          width="262"
          height="162"
          aria-hidden="true"
        />
        <Button color="primary" onClick={onSubscribe}>
          Activer
        </Button>
        <Button onClick={onDismiss}>Pas maintenant</Button>
        <footer>Vous pourrez changer à tout moment</footer>
        {subscriptionError && (
          <footer style={{ color: style.redNSP }}>{subscriptionError}</footer>
        )}
      </StyledWrapper>
    </>
  );
};
DeviceNotificationSubscription.propTypes = {
  onSubscribe: PropTypes.func.isRequired,
  onDismiss: PropTypes.func.isRequired,
  subscriptionError: PropTypes.string,
};
export default DeviceNotificationSubscription;
