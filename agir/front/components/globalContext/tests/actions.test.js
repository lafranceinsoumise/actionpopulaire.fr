import ACTION_TYPE from "../actionTypes";
import createDispatch, * as actions from "../actions";

jest.mock("@agir/activity/common/helpers");

const mockDispatch = jest.fn();
const dispatch = createDispatch(mockDispatch);

describe("GlobalContext/actions", function () {
  beforeEach(function () {
    mockDispatch.mockReset();
  });
  describe("initFromScriptTag action creator", function () {
    it(`should dispatch an action of type ${ACTION_TYPE.INIT_ACTION}`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      dispatch(actions.initFromScriptTag());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.INIT_ACTION
      );
    });
    it(`should add the backend generated globalContext object properties to dispatched action payload`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const globalContext = {
        some: "prop",
      };
      const globalContextScript = document.createElement("div");
      globalContextScript.id = "globalContext";
      globalContextScript.textContent = JSON.stringify(globalContext);
      document.body.appendChild(globalContextScript);

      dispatch(actions.initFromScriptTag());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.INIT_ACTION
      );
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty("some", "prop");
    });
    it(`should add the backend generated extraContext object properties to dispatched action payload`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const extraContext = {
        extra: "prop",
      };
      const extraContextScript = document.createElement("div");
      extraContextScript.id = "extraContext";
      extraContextScript.textContent = JSON.stringify(extraContext);
      document.body.appendChild(extraContextScript);

      dispatch(actions.initFromScriptTag());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.INIT_ACTION
      );
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty("extra", "prop");
    });
    it(`should let extraContext data override globalContext data`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const globalContext = {
        some: "prop",
      };
      const globalContextScript = document.createElement("div");
      globalContextScript.id = "globalContext";
      globalContextScript.textContent = JSON.stringify(globalContext);
      document.body.appendChild(globalContextScript);

      const extraContext = {
        extra: "prop",
      };
      const extraContextScript = document.createElement("div");
      extraContextScript.id = "extraContext";
      extraContextScript.textContent = JSON.stringify(extraContext);
      document.body.appendChild(extraContextScript);

      dispatch(actions.initFromScriptTag());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.INIT_ACTION
      );
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty("extra", "prop");
    });
  });
  describe("setIs2022 action creator", function () {
    it(`should dispatch an action of type ${ACTION_TYPE.SET_IS_2022_ACTION}`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      dispatch(actions.setIs2022());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.SET_IS_2022_ACTION
      );
    });
  });
  describe("createDispatch function factory", function () {
    it("should return a function", function () {
      const dispatch = createDispatch(() => {});
      expect(typeof dispatch).toBe("function");
    });
    it("should return a function that accepts an action object", function () {
      const originalDispatch = jest.fn();
      const dispatch = createDispatch(originalDispatch);
      const action = {
        type: "some-action",
      };
      expect(originalDispatch.mock.calls).toHaveLength(0);
      dispatch(action);
      expect(originalDispatch.mock.calls).toHaveLength(1);
      expect(originalDispatch.mock.calls[0][0]).toEqual(action);
    });
    it("should return a function that accepts an action creator function", function () {
      const originalDispatch = jest.fn();
      const dispatch = createDispatch(originalDispatch);
      const actionCreator = jest.fn();
      expect(originalDispatch.mock.calls).toHaveLength(0);
      expect(actionCreator.mock.calls).toHaveLength(0);
      dispatch(actionCreator);
      expect(actionCreator.mock.calls).toHaveLength(1);
      expect(actionCreator.mock.calls[0][0]).toEqual(originalDispatch);
    });
  });
});
