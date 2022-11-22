import { useCallback, useEffect, useState } from "react";
import useSWR from "swr";

import CONFIG from "@agir/donations/common/config";
import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";
import * as api from "@agir/donations/common/api";

import {
  INITIAL_DATA,
  setFormDataForUser,
  validateDonationData,
} from "@agir/donations/common/form.config";

export const useDonations = (type = CONFIG.default.type, defaults = {}) => {
  const config = CONFIG[type] || CONFIG.default;

  const [isLoading, setIsLoading] = useState(false);
  const { data: session } = useSWR(
    "/api/session/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const [formData, setFormData] = useState({
    ...INITIAL_DATA,
    ...defaults,
    to: type,
    paymentTiming: Object.keys(config.allowedPaymentModes)[0],
  });
  const [formErrors, setFormErrors] = useState({});

  const updateFormData = useCallback((field, value) => {
    setFormErrors((currentErrors) => ({
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
      setFormErrors({});
      const donation = {
        ...formData,
        paymentMode,
      };
      let validationErrors = validateDonationData(donation);
      if (donation.nationality !== "FR" && donation.locationCountry !== "FR") {
        validationErrors = {
          ...(validationErrors || {}),
          locationCountry: "Veuillez indiquer votre adresse fiscale en France.",
        };
      }

      if (validationErrors) {
        setIsLoading(false);
        setFormErrors(validationErrors);
        return;
      }
      const { data, error } = await api.createDonation(donation);
      setIsLoading(false);
      if (error) {
        setFormErrors(error);
        return;
      }

      window.location.href = data.next;
    },
    [formData]
  );

  useEffect(() => {
    if (!session) {
      return;
    }
    setFormData(setFormDataForUser(session?.user || {}));
  }, [session]);

  return {
    config,
    formData,
    formErrors,
    sessionUser:
      typeof session === "undefined" ? undefined : session?.user || null,
    isLoading,
    updateFormData,
    handleSubmit,
  };
};
