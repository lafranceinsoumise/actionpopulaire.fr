export const setUpNotificationsCenter = async function (
  element,
  notifications
) {
  const [
    { default: React },
    { default: ReactDOM },
    { default: NotificationsCenter },
  ] = await Promise.all([
    import("react"),
    import("react-dom"),
    import("./NotificationsCenter"),
  ]);

  ReactDOM.render(
    <NotificationsCenter notifications={notifications} />,
    element
  );
};
