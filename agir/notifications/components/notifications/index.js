export const setUpNotificationsCenter = async function (
  element,
  notifications
) {
  const [
    { default: React },
    { renderReactComponent },
    { default: NotificationsCenter },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./NotificationsCenter"),
  ]);

  renderReactComponent(
    <NotificationsCenter notifications={notifications} />,
    element
  );
};
