import { useEffect, useMemo, useState } from "react";
import useSWRImmutable from "swr/immutable";

import {
  getAuthenticationEndpoint,
  updateProfile,
} from "@agir/front/authentication/api";
import {
  useCustomCompareEffect,
  useDebounce,
  useUpdateEffect,
} from "react-use";
// import { useDebounce, useThrottle } from "@agir/lib/utils/hooks";

export const EVENT_TYPES = {
  nearEvents: "suggestions pour moi",
  groupEvents: "dans mes groupes",
  ongoingEvents: "en cours",
  pastEvents: "passés",
  organizedEvents: "organisés",
};

const ENDPOINT = {
  rsvpedEvents: "/api/evenements/rsvped/",
  nearEvents: "/api/evenements/suggestions/",
  groupEvents: "/api/evenements/mes-groupes/",
  ongoingEvents: "/api/evenements/rsvped/en-cours/",
  pastEvents: "/api/evenements/rsvped/passes/",
  organizedEvents: "/api/evenements/organises/",
  grandEvents: "/api/evenements/grands-evenements/",
};

export const getAgendaEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

const ACTION_RADIUS_MIN = 1;
const ACTION_RADIUS_MAX = 500;

const useActionRadius = (initialValue) => {
  const { data, mutate, isLoading } = useSWRImmutable(
    getAuthenticationEndpoint("getProfile"),
  );
  const { actionRadius: remoteValue, hasLocation = false } = data || {};
  const [localValue, setLocalValue] = useState(initialValue);
  const [debouncedLocalValue, setDebouncedLocalValue] = useState(initialValue);

  useDebounce(
    () => {
      let radius = parseInt(localValue);
      radius = radius && !isNaN(radius) ? parseInt(radius) : null;
      if (
        radius &&
        radius >= ACTION_RADIUS_MIN &&
        radius <= ACTION_RADIUS_MAX
      ) {
        setDebouncedLocalValue(localValue);
      }
    },
    500,
    [localValue],
  );

  const actionRadiusRangeProps = useMemo(
    () => ({
      value: hasLocation ? localValue : null,
      onChange: setLocalValue,
      disabled: isLoading,
      remoteValue,
      min: ACTION_RADIUS_MIN,
      max: ACTION_RADIUS_MAX,
    }),
    [hasLocation, localValue, setLocalValue, isLoading, remoteValue],
  );

  useUpdateEffect(() => {
    if (
      isLoading ||
      !debouncedLocalValue ||
      debouncedLocalValue === remoteValue
    ) {
      return;
    }
    mutate(
      async (userProfile) => {
        const { data, error } = await updateProfile({
          actionRadius: debouncedLocalValue,
        });
        return data && !error
          ? data
          : { ...userProfile, actionRadius: debouncedLocalValue };
      },
      { revalidate: false },
    );
  }, [mutate, isLoading, debouncedLocalValue, remoteValue]);

  return actionRadiusRangeProps;
};

export const useEventSuggestions = (isPaused = false) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeKey = Object.keys(EVENT_TYPES)[activeIndex];

  const { data: session } = useSWRImmutable("/api/session/");
  const { data: events, mutate } = useSWRImmutable(
    activeKey && getAgendaEndpoint(activeKey),
    { isPaused },
  );
  const { data: grandEvents } = useSWRImmutable(
    getAgendaEndpoint("grandEvents"),
  );
  const { remoteValue: userActionRadius, ...actionRadiusRangeProps } =
    useActionRadius(session?.user?.actionRadius);

  const userID = session?.user && session.user.id;
  const userZip = session?.user && session.user.zip;

  useCustomCompareEffect(
    () => {
      mutate({ optimisticData: undefined });
    },
    [userID, userZip, userActionRadius, mutate],
    (previous, next) =>
      !Object.keys(previous).some(
        (key) => previous[key] && previous[key] !== next[key],
      ),
  );

  return [
    Object.values(EVENT_TYPES),
    activeKey,
    activeIndex,
    setActiveIndex,
    events,
    grandEvents,
    actionRadiusRangeProps,
  ];
};
