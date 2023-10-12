import { useCallback, useEffect, useMemo, useState } from "react";
import useSWRImmutable from "swr/immutable";

import CONFIG from "@agir/donations/common/config";
import * as api from "@agir/donations/common/api";
import {
  getReminder,
  parseAllocations,
} from "@agir/donations/common/allocations.config";

import {
  INITIAL_DATA,
  setFormDataForUser,
  validateContributionRenewal,
  validateDonationData,
} from "@agir/donations/common/form.config";

export const useGroupDonation = (initialGroupPk, isActive = true) => {
  const [isReady, setIsReady] = useState(false);
  const { data: initialGroup, isValidating: isGroupLoading } = useSWRImmutable(
    isActive && initialGroupPk && `/api/groupes/${initialGroupPk}/`,
  );
  const { data: groups, isValidating: areGroupsLoading } = useSWRImmutable(
    isActive && `/api/groupes/`,
  );

  const [selectedGroup, setSelectedGroup] = useState(null);

  const groupOptions = useMemo(() => {
    if (!Array.isArray(groups)) {
      return [];
    }
    const options = groups.filter((g) => g.isCertified);
    if (
      options.length === 0 ||
      !initialGroup?.isCertified ||
      options.find((g) => g.id === initialGroup.id)
    ) {
      return options;
    }

    return [initialGroup, ...options];
  }, [groups, initialGroup]);

  useEffect(() => {
    !isReady && !areGroupsLoading && !isGroupLoading && setIsReady(true);
  }, [isReady, areGroupsLoading, isGroupLoading]);

  useEffect(() => {
    initialGroup &&
      initialGroup.isCertified &&
      !selectedGroup &&
      setSelectedGroup(initialGroup);
  }, [initialGroup, selectedGroup]);

  return {
    group: selectedGroup,
    groups: groupOptions,
    isGroupReady: isReady,
    selectGroup: setSelectedGroup,
  };
};

export const useDonations = (
  type = CONFIG.default.type,
  initialGroupPk,
  defaults = {},
) => {
  const config = CONFIG[type] || CONFIG.default;

  const [isReady, setIsReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { data: session, isValidating: isSessionLoading } =
    useSWRImmutable("/api/session/");
  const [formData, setFormData] = useState({
    ...INITIAL_DATA,
    ...defaults,
    to: config.type,
    paymentTiming: Object.keys(config.allowedPaymentModes)[0],
    endDate:
      typeof config.getEndDate === "function" ? config.getEndDate() : null,
  });

  const { group, groups, isGroupReady, selectGroup } = useGroupDonation(
    initialGroupPk,
    config.hasAllocations,
  );

  const [formErrors, setErrors] = useState({});

  const updateFormData = useCallback((field, value) => {
    setErrors((currentErrors) => ({
      ...currentErrors,
      [field]: "",
    }));

    setFormData((current) => ({
      ...current,
      [field]: value,
    }));
  }, []);

  const handleSubmit = useCallback(
    async (paymentMode) => {
      setIsLoading(true);
      setErrors({});
      const donation = {
        ...formData,
        paymentMode,
      };
      let validationErrors = validateDonationData(donation);
      if (getReminder(formData?.allocations, formData.amount)) {
        validationErrors = {
          ...(validationErrors || {}),
          global:
            "La somme des des allocations est différente du montant total",
        };
      }
      if (donation.nationality !== "FR" && donation.locationCountry !== "FR") {
        validationErrors = {
          ...(validationErrors || {}),
          locationCountry: "Veuillez indiquer votre adresse fiscale en France.",
        };
      }

      if (validationErrors) {
        setIsLoading(false);
        setErrors(validationErrors);
        return;
      }
      const { data, error } = await api.createDonation(donation);
      setIsLoading(false);
      if (error) {
        setErrors(error);
        return;
      }

      window.location.href = data.next;
    },
    [formData],
  );

  useEffect(() => {
    if (!session) {
      return;
    }
    setFormData(setFormDataForUser(session?.user || {}));
  }, [session]);

  useEffect(() => {
    if (!group?.location?.departement) {
      return;
    }
    updateFormData("departement", group.location.departement);
  }, [group, updateFormData]);

  useEffect(() => {
    !isReady && !isSessionLoading && isGroupReady && setIsReady(true);
  }, [isReady, isSessionLoading, isGroupReady]);

  return {
    config,
    formData,
    formErrors,
    sessionUser: session?.user || null,
    group,
    groups,
    isReady,
    isLoading,
    updateFormData,
    handleSubmit,
    selectGroup,
  };
};

export const useContributionRenewal = (type = CONFIG.contribution.type) => {
  const config = CONFIG[type] || CONFIG.default;

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const { data: session, isLoading: isSessionLoading } =
    useSWRImmutable("/api/session/");

  const { data: activeContribution, isLoading: isActiveContributionLoading } =
    useSWRImmutable(api.getDonationEndpoint("getActiveContribution"));

  const endDate =
    typeof config.getEndDate === "function" ? config.getEndDate() : null;

  const [allocations, inactiveGroupAllocation] = useMemo(
    () => parseAllocations(activeContribution),
    [activeContribution],
  );

  const group = useMemo(() => {
    const groupAllocation = allocations.find(
      (allocation) => !!allocation.group,
    );
    return groupAllocation && groupAllocation?.group;
  }, [allocations]);

  const handleSubmit = useCallback(async () => {
    setIsLoading(true);
    setErrors({});
    const newContribution = {
      ...activeContribution,
      endDate,
      allocations,
    };

    let validationErrors = validateContributionRenewal(newContribution);

    if (getReminder(newContribution?.allocations, newContribution.amount)) {
      validationErrors = {
        ...(validationErrors || {}),
        global: "La somme des des allocations est différente du montant total",
      };
    }

    if (
      newContribution.nationality !== "FR" &&
      newContribution.locationCountry !== "FR"
    ) {
      validationErrors = {
        ...(validationErrors || {}),
        locationCountry: "Veuillez indiquer votre adresse fiscale en France.",
      };
    }

    if (validationErrors) {
      setIsLoading(false);
      setErrors(validationErrors);
      return;
    }
    const { data, error } = await api.createDonation(newContribution);
    setIsLoading(false);

    if (error) {
      setErrors(error);
      return;
    }

    window.location.href = data.next;
  }, [activeContribution, endDate, allocations]);

  return {
    config,
    activeContribution,
    endDate,
    allocations,
    inactiveGroupAllocation,
    group,
    errors, //: "Une erreur est survenue",
    user: session?.user || null,
    isReady: !isSessionLoading && !isActiveContributionLoading,
    isLoading,
    onSubmit: handleSubmit,
  };
};
