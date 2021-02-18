export const DEFAULT_FORM_DATA = {
  name: "",
  organizerGroup: "",
  startTime: new Date().toUTCString(),
  endTime: new Date().toUTCString(),
  subtype: null,
  location: {
    name: "",
    address1: "",
    address2: "",
    city: "",
    zip: "",
    country: "",
  },
  contact: {
    name: "Jane Doe",
    email: "janedoe@gmail.com",
    phone: "0600000000",
    hidePhone: false,
  },
};

export const EVENT_DEFAULT_DURATIONS = [
  {
    value: 60,
    label: "1h",
  },
  {
    value: 90,
    label: "1h30",
  },
  {
    value: 120,
    label: "2h",
  },
  {
    value: 180,
    label: "3h",
  },
  {
    value: null,
    label: "Personnalisée",
  },
];
