import React from "react";
import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import TellMoreProvider from "./TellMoreContext";

const TellMorePage = () => {
  return (
    <>
      <TellMoreProvider>
        <ChooseCampaign />
        <TellMore />
      </TellMoreProvider>
    </>
  );
};

export default TellMorePage;
