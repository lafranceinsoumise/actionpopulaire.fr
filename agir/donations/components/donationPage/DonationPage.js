import React, { useCallback, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import Helmet from "react-helmet";
import useSWR from "swr";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import AmountStep from "./AmountStep";
import { Theme } from "./StyledComponents";
import CONFIG from "./config";
import * as api from "./api";

const DonationPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const { data: session } = useSWR("/api/session/");

  const params = useParams();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const type = params?.type || "LFI";
  const groupPk = type !== "2022" && urlParams.get("group");

  const { data: group } = useSWR(groupPk && `/api/groupes/${groupPk}/`, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  const { data: userGroups } = useSWR(
    session?.user && type !== "2022" && "/api/groupes/",
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  const [formData, setFormData] = useState({
    // amounts
    amount: 500,
    to: type,
    type: "S",
    allocations: [],
    // informations
    email: session?.user?.email || "",
    first_name: session?.user?.firstName || "",
    last_name: "",
    contact_phone: "",
    nationality: "FR",
    location_address1: "",
    location_zip: "",
    location_city: "",
    location_country: "FR",
    // checkboxes
    subscribed_lfi: false,
    consent_certification: false,
    french_resident: true,
    // mode
    payment_mode: "system_pay",
  });

  const handleAmountSubmit = useCallback(async (data) => {
    setIsLoading(true);
    setErrors({});

    const { data: result, error } = await api.createDonation(data);

    setFormData({
      ...formData,
      ...result,
    });
    setIsLoading(false);

    if (error) {
      setErrors({
        amount: error?.amount || "Une erreur est survenue. Veuillez ressayer.",
      });
      return;
    }

    // Keep group param in url
    window.location.href = result.next + (!!groupPk ? `?group=${groupPk}` : "");
  }, []);

  return (
    <Theme type={formData.to}>
      <Helmet>
        <title>{CONFIG[type]?.title || CONFIG.default.title}</title>
      </Helmet>
      <PageFadeIn ready={typeof session !== "undefined"} wait={<Skeleton />}>
        <AmountStep
          type={type}
          maxAmount={CONFIG[type]?.maxAmount || CONFIG.default.maxAmount}
          maxAmountWarning={
            CONFIG[type]?.maxAmountWarning || CONFIG.default.maxAmountWarning
          }
          externalLinkRoute={
            CONFIG[type]?.externalLinkRoute || CONFIG.default.externalLinkRoute
          }
          group={group && group.isCertified ? group : null}
          hasGroups={
            Array.isArray(userGroups?.groups) &&
            userGroups.groups.some((group) => group.isCertified)
          }
          isLoading={isLoading}
          error={errors?.amount}
          onSubmit={handleAmountSubmit}
        />
      </PageFadeIn>
    </Theme>
  );
};

export default DonationPage;
