import PropTypes from "prop-types";
import React from "react";
import GroupCertification from "./GroupCertification";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import { useGroup } from "@agir/groups/groupPage/hooks/group";

const GroupLinksPage = (props) => {
  const { onBack, illustration, groupPk } = props;

  const group = useGroup(groupPk);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <PageFadeIn ready={!!group} wait={<Skeleton />}>
        {group && (
          <GroupCertification
            routes={group.routes}
            isCertified={group.isCertified}
            certificationCriteria={group.certificationCriteria}
          />
        )}
      </PageFadeIn>
    </>
  );
};
GroupLinksPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupLinksPage;
