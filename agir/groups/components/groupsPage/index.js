import { renderWithContext } from "@agir/lib/utils/react";

renderWithContext(import("./GroupsPage").then((module) => module.default));
