import React, { Suspense, useMemo, useState } from "react";

import { lazy } from "@agir/front/app/utils";
import { useMissingRequiredEventDocuments } from "@agir/events/common/hooks";

import MissingDocumentWarning from "./MissingDocumentWarning";

const MissingDocumentModal = lazy(() => import("./MissingDocumentModal"));

const MissingDocuments = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { projects } = useMissingRequiredEventDocuments();
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
    return projects.map((project) => project.limitDate).sort()[0];
  }, [projects]);

  const isBlocked = useMemo(() => {
    if (!Array.isArray(projects) || projects.length === 0) {
      return false;
    }
    return projects.some((project) => project.isBlocking);
  }, [projects]);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <>
      <MissingDocumentWarning
        missingDocumentCount={missingDocumentCount}
        limitDate={limitDate}
        onClick={openModal}
      />
      <Suspense fallback={null}>
        <MissingDocumentModal
          shouldShow={isModalOpen}
          projects={projects}
          onClose={closeModal}
          isBlocked={isBlocked}
        />
      </Suspense>
    </>
  );
};

export default MissingDocuments;
