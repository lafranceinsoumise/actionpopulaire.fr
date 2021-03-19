import React, { createContext, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { getProfile } from "@agir/front/authentication/api";

export const TellMoreContext = createContext(null);

const TellMoreProvider = ({ children }) => {
  const [infos, setInfos] = useState({});
  const [page, setPage] = useState(0);

  const getProfileInfos = async () => {
    const data = await getProfile();
    console.log("data : ", data);
    // setInfos(data);
    // if (data.isInsoumise || data.is2022) setPage(1);
  };

  useEffect(() => {
    getProfileInfos();
  }, []);

  return (
    <TellMoreContext.Provider value={{ infos, setInfos, page, setPage }}>
      {children}
    </TellMoreContext.Provider>
  );
};

TellMoreProvider.propTypes = {
  children: PropTypes.node,
};

TellMoreProvider.defaultProps = {
  children: <></>,
};

export default TellMoreProvider;
