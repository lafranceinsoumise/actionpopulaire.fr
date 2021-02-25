import "./style.css";
import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: CreateGroupForm },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("./createGroupForm"),
  ]);

  const render = (Component) => (id, props = {}) => {
    renderReactComponent(<Component {...props} />, document.getElementById(id));
  };

  const renderCreateGroupForm = render(CreateGroupForm);

  function onLoad() {
    const reactJsonScript = document.getElementById("react-json-script");
    let reactAppProps = null;
    if (reactJsonScript && reactJsonScript.type === "application/json") {
      reactAppProps = JSON.parse(reactJsonScript.textContent);
    }

    if (document.getElementById("create-group-react-app")) {
      renderCreateGroupForm("create-group-react-app", reactAppProps || {});
    }
  }

  onDOMReady(onLoad);
})();
