import { Helmet } from "react-helmet";
import React from "react";

import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import { SWRConfig } from "swr";
import axios from "@agir/lib/utils/axios";

import PushModal from "@agir/front/allPages/PushModal/PushModal";

import Router from "./Router";

const fetcher = async (url) => {
  const res = await axios.get(url);
  return res.data;
};

export default function App() {
  return (
    <SWRConfig
      value={{
        fetcher,
        onErrorRetry: (error) => {
          if ([403, 404, 410].includes(error.status)) return;
        },
      }}
    >
      <GlobalContextProvider hasRouter hasToasts>
        <Router>
          <Helmet>
            <title>Action Populaire</title>
          </Helmet>
          <PushModal isActive />
        </Router>
      </GlobalContextProvider>
    </SWRConfig>
  );
}
