const tabs = [
  {
    id: "info",
    slug: "presentation",
    label: "Présentation",
    isActive: (_, isMobile) => !!isMobile,
  },
  {
    id: "agenda",
    slug: "agenda",
    label: "Agenda",
    isActive: ({ pastEvents, upcomingEvents }, isMobile) => {
      if (!isMobile) {
        return true;
      }
      pastEvents = Array.isArray(pastEvents) ? pastEvents : [];
      upcomingEvents = Array.isArray(upcomingEvents) ? upcomingEvents : [];
      return pastEvents.length + upcomingEvents.length > 0;
    },
  },
  {
    id: "reports",
    slug: "comptes-rendus",
    label: "Comptes-rendus",
    isActive: ({ pastEventReports }) =>
      Array.isArray(pastEventReports) && pastEventReports.length > 0,
  },
];

export default tabs;
