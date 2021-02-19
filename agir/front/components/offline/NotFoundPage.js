import React, { useEffect } from "react";

import illustration from "./illustration.svg";
import styled from "styled-components";
import useSWR from "swr";
import { useIsOffline } from "@agir/front/offline/hooks";

const PageStyle = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: calc(80vh);

  & > * {
    margin: 0 auto;
    padding: 0 16px;
  }

  & > h1 {
    font-size: 20px;
  }
`;

// Most of the time, if we are in the app on unknow URL, it is because of service worker no network handling
const NotFoundPage = () => {
  const isOffline = useIsOffline();

  // We try to reload every 5 second
  useEffect(() => {
    if (!isOffline) {
      return;
    }

    setTimeout(() => {
      window.location.reload();
    }, 5000);
  }, [isOffline]);

  if (isOffline === null) return null;

  return (
    <PageStyle>
      {isOffline ? (
        <>
          <img src={illustration} style={{ marginBottom: "32px" }} />
          <h1 style={{ marginBottom: "8px" }}>Pas de connexion</h1>
          <p>
            Connectez-vous à un
            <br />
            réseau Wi-Fi ou mobile
          </p>
        </>
      ) : (
        <h1>Page introuvable</h1>
      )}
    </PageStyle>
  );
};
export default NotFoundPage;
