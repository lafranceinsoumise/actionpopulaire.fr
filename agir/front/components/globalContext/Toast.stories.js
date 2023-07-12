import React from "react";
import shortUUID from "short-uuid";

import { Toast, TOAST_TYPES } from "./Toast";

export default {
  component: Toast,
  title: "GlobalContext/Toast",
  argTypes: {
    toasts: { table: { disable: true } },
    onClear: { table: { disable: true } },
    type: {
      control: {
        type: "select",
        options: Object.keys(TOAST_TYPES),
      },
    },
  },
};

const Template = ({ message, html, type }) => {
  const [toasts, setToasts] = React.useState([]);
  const onClear = React.useCallback((t) => {
    setToasts((state) => state.filter(({ toastId }) => t.toastId !== toastId));
  }, []);
  React.useEffect(
    () =>
      setToasts((state) => [
        ...state,
        {
          toastId: shortUUID.generate(),
          message,
          html,
          type,
        },
      ]),
    [message, type],
  );
  return <Toast onClear={onClear} toasts={toasts} />;
};

export const Default = Template.bind({});
Default.args = {
  message: 'Toast ! <a href="#"><b>Avec</b> un lien</a>.',
  html: true,
  type: Object.keys(TOAST_TYPES)[0],
};
