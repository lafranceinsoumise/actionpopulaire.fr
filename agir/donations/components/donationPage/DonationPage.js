import React, { useCallback, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import useSWR from "swr";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import AmountStep from "./AmountStep";

import { createDonation } from "./api";

const DonationPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const { data: session } = useSWR("/api/session/");

  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const type = params?.type || "LFI";
  const groupPk = type !== "melenchon2022" && urlParams.get("group");

  const { data: group } = useSWR(groupPk && `/api/groupes/${groupPk}/`, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const { data: userGroups } = useSWR(
    session?.user && type !== "melenchon2022" && "/api/groupes/",
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  const handleSubmit = useCallback(async (data) => {
    setIsLoading(true);
    setError("");
    const result = await createDonation(data);
    setIsLoading(false);
    if (result.error || !result?.data?.next) {
      setError(result.error || "Une erreur est survenue. Veuillez ressayer.");
      return;
    }
    window.location.href = result.data.next;
  }, []);

  return (
    <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
      <AmountStep
        type={type}
        group={group && group.isCertified ? group : null}
        hasGroups={
          Array.isArray(userGroups?.groups) &&
          userGroups.groups.some((group) => group.isCertified)
        }
        isLoading={isLoading}
        error={error}
        onSubmit={handleSubmit}
      />
    </PageFadeIn>
  );
};

export default DonationPage;
