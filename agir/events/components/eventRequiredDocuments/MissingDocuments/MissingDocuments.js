import _sortBy from "lodash/sortBy";
import React, { Suspense, useMemo } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";

import { lazy } from "@agir/front/app/utils";
import { routeConfig } from "@agir/front/app/routes.config";
import { useMissingRequiredEventDocuments } from "@agir/events/common/hooks";

import MissingDocumentWarning from "./MissingDocumentWarning";

const MissingDocumentModal = lazy(() => import("./MissingDocumentModal"));

const MissingDocuments = () => {
  const history = useHistory();
  const { projects } = useMissingRequiredEventDocuments();
  const modalRouteMatch = useRouteMatch(
    routeConfig.missingEventDocumentModal.path
  );

  const missingDocumentCount = useMemo(() => {
    if (!Array.isArray(projects)) {
      return 0;
    }
    return projects.reduce(
      (count, project) => (count += project.missingDocumentCount),
      0
    );
  }, [projects]);

  const limitDate = useMemo(() => {
    if (!Array.isArray(projects) || projects.length === 0) {
      return null;
    }
    return _sortBy(projects, ["limitDate"])[0].limitDate;
  }, [projects]);

  const closeModal = () => history.push(routeConfig.events.getLink());

  return (
    <>
      <MissingDocumentWarning
        missingDocumentCount={missingDocumentCount}
        limitDate={limitDate}
      />
      <Suspense fallback={null}>
        <MissingDocumentModal
          shouldShow={!!modalRouteMatch}
          projects={projects}
          onClose={closeModal}
        />
      </Suspense>
    </>
  );
};

export default MissingDocuments;
