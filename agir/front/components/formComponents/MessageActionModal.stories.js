import React from "react";
import MessageActionModal from "./MessageActionModal";

export default {
  component: MessageActionModal,
  title: "Form/MessageActionModal",
};

const Template = (args) => {
  const [action, setAction] = React.useState(args.action);
  const [shouldShow, setShouldShow] = React.useState(true);
  const [isLoading, setIsLoading] = React.useState(false);
  const mockAction = React.useMemo(
    () => (action) =>
      action
        ? async () => {
            setIsLoading(true);
            action();
            await new Promise((resolve) => {
              setTimeout(() => {
                setIsLoading(false);
                resolve();
              }, 2000);
            });
          }
        : undefined,
    [],
  );
  const handleDelete = mockAction(args.onDelete);
  const handleReport = mockAction(args.onReport);

  return (
    <>
      {!shouldShow ? (
        <button
          onClick={() => {
            setShouldShow(true);
            setAction(args.action);
          }}
        >
          {args.action.toUpperCase()}
        </button>
      ) : null}
      <MessageActionModal
        {...args}
        action={action}
        onClose={() => {
          setShouldShow(false);
          setAction("");
        }}
        shouldShow={shouldShow}
        onDelete={handleDelete}
        onReport={handleReport}
        isLoading={isLoading}
      />
    </>
  );
};

export const DeleteAndReport = Template.bind({});
DeleteAndReport.args = {
  action: "delete",
  isLoading: false,
};

export const DeleteOnly = Template.bind({});
DeleteOnly.args = {
  action: "delete",
  onReport: undefined,
  isLoading: false,
};

export const ReportAndDelete = Template.bind({});
ReportAndDelete.args = {
  action: "report",
  isLoading: false,
};

export const ReportOnly = Template.bind({});
ReportOnly.args = {
  action: "report",
  onDelete: undefined,
  isLoading: false,
};
