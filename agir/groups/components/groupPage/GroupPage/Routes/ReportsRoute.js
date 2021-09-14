import { Helmet } from "react-helmet";
import PropTypes from "prop-types";
import React from "react";

import { EmptyReports } from "@agir/groups/groupPage/EmptyContent";
import GroupEventList from "@agir/groups/groupPage/GroupEventList";

const ReportsRoute = ({ group, pastEventReports }) => (
  <>
    <Helmet>
      <title>Comptes rendus du groupe : {group.name} - Action populaire</title>
    </Helmet>
    {Array.isArray(pastEventReports) && pastEventReports.length === 0 ? (
      <EmptyReports />
    ) : (
      <GroupEventList title="Comptes rendus" events={pastEventReports} />
    )}
  </>
);

ReportsRoute.propTypes = {
  group: PropTypes.shape({
    name: PropTypes.string,
  }),
  pastEventReports: PropTypes.arrayOf(PropTypes.object),
};

export default ReportsRoute;
