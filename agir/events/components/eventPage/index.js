import { renderWithContext } from "@agir/lib/utils/react";

renderWithContext(import("./EventPage").then((module) => module.default));
