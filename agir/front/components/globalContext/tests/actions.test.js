import ACTION_TYPE from "../actionTypes";
import createDispatch, * as actions from "../actions";

jest.mock("@agir/activity/common/helpers");

const mockDispatch = jest.fn();
const dispatch = createDispatch(mockDispatch);

describe("GlobalContext/actions", function () {
  beforeEach(function () {
    mockDispatch.mockReset();
  });
  describe("init action creator", function () {
    it(`should dispatch an action of type ${ACTION_TYPE.INIT_ACTION}`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      dispatch(actions.init());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.INIT_ACTION
      );
    });
  });
  describe("setisPoliticalSupport action creator", function () {
    it(`should dispatch an action of type ${ACTION_TYPE.SET_IS_POLITICAL_SUPPORT_ACTION}`, function () {
      expect(mockDispatch.mock.calls).toHaveLength(0);
      dispatch(actions.setisPoliticalSupport());
      expect(mockDispatch.mock.calls).toHaveLength(1);
      expect(mockDispatch.mock.calls[0][0]).toHaveProperty(
        "type",
        ACTION_TYPE.SET_IS_POLITICAL_SUPPORT_ACTION
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
