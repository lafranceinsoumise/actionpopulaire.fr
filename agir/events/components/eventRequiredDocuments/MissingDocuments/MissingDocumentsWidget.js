import React, { Suspense, useMemo } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";

import { lazy } from "@agir/front/app/utils";
import { routeConfig } from "@agir/front/app/routes.config";
import { useMissingRequiredEventDocuments } from "@agir/events/common/hooks";

import MissingDocumentWarning from "./MissingDocumentWarning";

const MissingDocumentModal = lazy(() => import("./MissingDocumentModal"));

const MissingDocuments = () => {
  const history = useHistory();
  const routeMatch = useRouteMatch(routeConfig.missingEventDocumentsModal.path);

  const { projects } = useMissingRequiredEventDocuments();

  const missingDocumentCount = useMemo(() => {
    if (!Array.isArray(projects)) {
      return 0;
    }
    return projects.reduce(
      (count, project) => (count += project.missingDocumentCount),
      0,
    );
  }, [projects]);

  const limitDate = useMemo(() => {
    if (!Array.isArray(projects) || projects.length === 0) {
      return null;
    }
    return projects.map((project) => project.limitDate).sort()[0];
  }, [projects]);

  const isBlocked = useMemo(() => {
    if (!Array.isArray(projects) || projects.length === 0) {
      return false;
    }
    return projects.some((project) => project.isBlocking);
  }, [projects]);

  const openModal = () =>
    history.push(routeConfig.missingEventDocumentsModal.getLink());
  const closeModal = () => history.push(routeConfig.events.getLink());

  if (!missingDocumentCount) {
    return null;
  }

  return (
    <>
      <MissingDocumentWarning
        missingDocumentCount={missingDocumentCount}
        limitDate={limitDate}
        onClick={openModal}
      />
      <Suspense fallback={null}>
        <MissingDocumentModal
          shouldShow={!!routeMatch}
          projects={projects}
          onClose={closeModal}
          isBlocked={isBlocked}
        />
      </Suspense>
    </>
  );
};

export default MissingDocuments;
