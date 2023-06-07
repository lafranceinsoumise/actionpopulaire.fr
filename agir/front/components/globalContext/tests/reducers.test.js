import ACTION_TYPE from "../actionTypes";

import * as activityHelpers from "@agir/activity/common/helpers";
import rootReducer, * as reducers from "../reducers";

describe("GlobalContext/reducers", function () {
  describe("isPoliticalSupport reducer", function () {
    it(`should return false by default if current state is undefined`, function () {
      const state = undefined;
      const action = {
        type: "unknown-action",
        user: { isPoliticalSupport: true },
      };
      const result = reducers.isPoliticalSupport(state, action);
      expect(result).toEqual(false);
    });
    it(`should return current state by default if defined`, function () {
      const state = true;
      const action = {
        type: "unknown-action",
        user: { isPoliticalSupport: false },
      };
      const result = reducers.isPoliticalSupport(state, action);
      expect(result).toEqual(state);
    });
    it(`should return false if action.user is not defined and action.type equals ${ACTION_TYPE.SET_SESSION_CONTEXT_ACTION}`, function () {
      const state = true;
      const action = {
        type: ACTION_TYPE.SET_SESSION_CONTEXT_ACTION,
        user: null,
      };
      const result = reducers.isPoliticalSupport(state, action);
      expect(result).toEqual(false);
    });
    it(`should return action.user.isPoliticalSupport if defined and action.type equals ${ACTION_TYPE.SET_SESSION_CONTEXT_ACTION}`, function () {
      const state = false;
      const action = {
        type: ACTION_TYPE.SET_SESSION_CONTEXT_ACTION,
        user: { isPoliticalSupport: true },
      };
      const result = reducers.isPoliticalSupport(state, action);
      expect(result).toEqual(action.user.isPoliticalSupport);
    });
  });
});
