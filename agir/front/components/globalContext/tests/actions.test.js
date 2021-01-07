import ACTION_TYPE from "../actionTypes";

import * as activityHelpers from "@agir/activity/common/helpers";
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
  describe("setActivityAsRead action creator", function () {
    it(`should dispatch an action of type ${ACTION_TYPE.SET_ACTIVITY_AS_READ_ACTION}`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      dispatch(actions.setActivityAsRead());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.SET_ACTIVITY_AS_READ_ACTION
      );
    });
  });
  describe("setAllActivitiesAsRead action creator", function () {
    afterEach(() => {
      activityHelpers.setActivitiesAsDisplayed.mockClear();
    });
    it("should call activity helper function 'setActivitiesAsDisplayed'", function () {
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      const ids = [1, 2, 3];
      dispatch(actions.setAllActivitiesAsRead(ids));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls[0][0]).toEqual(
        ids
      );
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION} if api calls rejects`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, true));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION} if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivitiesAsDisplayed.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, true));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION} if api calls succeeds but argument updateState is false`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, false));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
    });
    it(`should dispatch an action of type ${ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION} if api calls succeeds and argument updateState is true`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, true));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION
      );
    });
  });
  describe("dismissRequiredActionActivity action creator", function () {
    afterEach(() => {
      activityHelpers.setActivityAsInteracted.mockClear();
    });
    it("should call activity helper function 'setActivityAsInteracted'", function () {
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      const id = 10;
      dispatch(actions.dismissRequiredActionActivity(id));
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(activityHelpers.setActivityAsInteracted.mock.calls[0][0]).toEqual(
        id
      );
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION} if api calls rejects`, async function () {
      activityHelpers.setActivityAsInteracted.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const id = 10;
      await dispatch(actions.dismissRequiredActionActivity(id));
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION} if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivityAsInteracted.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const id = 10;
      await dispatch(actions.dismissRequiredActionActivity(id));
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should dispatch an action of type ${ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION} if api calls succeeds`, async function () {
      activityHelpers.setActivityAsInteracted.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const id = 10;
      await dispatch(actions.dismissRequiredActionActivity(id));
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.DISMISS_REQUIRED_ACTION_ACTIVITY_ACTION
      );
    });
  });
  describe("undoRequiredActionActivityDismissal action creator", function () {
    afterEach(() => {
      activityHelpers.setActivityAsDisplayed.mockClear();
    });
    it("should call activity helper function 'setActivityAsDisplayed'", function () {
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      const id = 10;
      dispatch(actions.undoRequiredActionActivityDismissal(id));
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls[0][0]).toEqual(
        id
      );
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.UNDO_REQUIRED_ACTION_ACTIVITY_DISMISSAL_ACTION} if api calls rejects`, async function () {
      activityHelpers.setActivityAsDisplayed.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const id = 10;
      await dispatch(actions.undoRequiredActionActivityDismissal(id));
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls).toHaveLength(0);
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.UNDO_REQUIRED_ACTION_ACTIVITY_DISMISSAL_ACTION} if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivityAsDisplayed.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const id = 10;
      await dispatch(actions.undoRequiredActionActivityDismissal(id));
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should dispatch an action of type ${ACTION_TYPE.UNDO_REQUIRED_ACTION_ACTIVITY_DISMISSAL_ACTION} if api calls succeeds`, async function () {
      activityHelpers.setActivityAsDisplayed.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const id = 10;
      await dispatch(actions.undoRequiredActionActivityDismissal(id));
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.UNDO_REQUIRED_ACTION_ACTIVITY_DISMISSAL_ACTION
      );
    });
  });
  describe("setAnnouncementsAsRead action creator", function () {
    afterEach(() => {
      activityHelpers.setActivitiesAsDisplayed.mockClear();
    });
    it("should call activity helper function 'setActivitiesAsDisplayed'", function () {
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      const ids = [1, 2, 3];
      dispatch(actions.setAllActivitiesAsRead(ids));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls[0][0]).toEqual(
        ids
      );
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.SET_ANNOUNCEMENTS_AS_READ_ACTION} if api calls rejects`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, true));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
    });
    it(`should not dispatch an action of type ${ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION} if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivitiesAsDisplayed.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, true));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should dispatch an action of type ${ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION} if api calls succeeds`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mockDispatch.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await dispatch(actions.setAllActivitiesAsRead(ids, true));
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.SET_ALL_ACTIVITIES_AS_READ_ACTION
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
