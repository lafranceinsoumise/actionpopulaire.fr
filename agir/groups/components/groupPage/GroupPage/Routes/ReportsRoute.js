import PropTypes from "prop-types";
import React from "react";

import { EmptyReports } from "@agir/groups/groupPage/EmptyContent";
import GroupEventList from "@agir/groups/groupPage/GroupEventList";

const ReportsRoute = ({ pastEventReports }) =>
  Array.isArray(pastEventReports) && pastEventReports.length === 0 ? (
    <EmptyReports />
  ) : (
    <GroupEventList title="Comptes-rendus" events={pastEventReports} />
  );

ReportsRoute.propTypes = {
  pastEventReports: PropTypes.arrayOf(PropTypes.object),
};

export default ReportsRoute;
