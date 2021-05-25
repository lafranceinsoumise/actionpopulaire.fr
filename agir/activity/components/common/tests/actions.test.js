import * as activityHelpers from "@agir/activity/common/helpers";
import {
  dismissRequiredActionActivity,
  setAllActivitiesAsRead,
  undoRequiredActionActivityDismissal,
} from "@agir/activity/common/actions";
import { mutate } from "swr";

jest.mock("@agir/activity/common/helpers");
jest.mock("swr");

describe("activity/actions", function () {
  describe("setAllActivitiesAsRead action creator", function () {
    afterEach(() => {
      activityHelpers.setActivitiesAsDisplayed.mockClear();
    });
    it("should call activity helper function 'setActivitiesAsDisplayed'", function () {
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      const ids = [1, 2, 3];
      setAllActivitiesAsRead(ids);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls[0][0]).toEqual(
        ids
      );
    });
    it(`should not call mutate if api calls rejects`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mutate.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await setAllActivitiesAsRead(ids);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mutate.mock.calls).toHaveLength(0);
    });
    it(`should not call mutate if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivitiesAsDisplayed.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mutate.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await setAllActivitiesAsRead(ids, true);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mutate.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should call mutate if api calls succeeds`, async function () {
      activityHelpers.setActivitiesAsDisplayed.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        0
      );
      expect(mutate.mock.calls).toHaveLength(0);
      const ids = [1, 2, 3];
      await setAllActivitiesAsRead(ids);
      expect(activityHelpers.setActivitiesAsDisplayed.mock.calls).toHaveLength(
        1
      );
      expect(mutate.mock.calls).toHaveLength(1);
      expect(mutate.mock.calls[0][0]).toEqual("/api/user/activities/");
    });
  });
  describe("dismissRequiredActionActivity action", function () {
    afterEach(() => {
      activityHelpers.setActivityAsInteracted.mockClear();
    });
    it("should call activity helper function 'setActivityAsInteracted'", function () {
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      const id = 10;
      dismissRequiredActionActivity(id);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(activityHelpers.setActivityAsInteracted.mock.calls[0][0]).toEqual(
        id
      );
    });
    it(`should not call mutate if api calls rejects`, async function () {
      activityHelpers.setActivityAsInteracted.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      expect(mutate.mock.calls).toHaveLength(0);
      const id = 10;
      await dismissRequiredActionActivity(id);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(mutate.mock.calls).toHaveLength(0);
    });
    it(`should not call mutate if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivityAsInteracted.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      expect(mutate.mock.calls).toHaveLength(0);
      const id = 10;
      await dismissRequiredActionActivity(id);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(mutate.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should call mutate if api calls succeeds`, async function () {
      activityHelpers.setActivityAsInteracted.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        0
      );
      expect(mutate.mock.calls).toHaveLength(0);
      const id = 10;
      await dismissRequiredActionActivity(id);
      expect(activityHelpers.setActivityAsInteracted.mock.calls).toHaveLength(
        1
      );
      expect(mutate.mock.calls).toHaveLength(1);
      expect(mutate.mock.calls[0][0]).toEqual("/api/user/required-activities/");
    });
  });
  describe("undoRequiredActionActivityDismissal action", function () {
    afterEach(() => {
      activityHelpers.setActivityAsDisplayed.mockClear();
    });
    it("should call activity helper function 'setActivityAsDisplayed'", function () {
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      const id = 10;
      undoRequiredActionActivityDismissal(id);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls[0][0]).toEqual(
        id
      );
    });
    it(`should not call mutate if api calls rejects`, async function () {
      activityHelpers.setActivityAsDisplayed.mockResolvedValueOnce(false);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      expect(mutate.mock.calls).toHaveLength(0);
      const id = 10;
      await undoRequiredActionActivityDismissal(id);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(mutate.mock.calls).toHaveLength(0);
    });
    it(`should not call mutate if api calls throws`, async function () {
      jest.spyOn(console, "log").mockReturnValueOnce();
      activityHelpers.setActivityAsDisplayed.mockRejectedValueOnce(
        new Error("Aïe!")
      );
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      expect(mutate.mock.calls).toHaveLength(0);
      const id = 10;
      await undoRequiredActionActivityDismissal(id);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(mutate.mock.calls).toHaveLength(0);
      console.log.mockRestore();
    });
    it(`should call mutate if api calls succeeds`, async function () {
      activityHelpers.setActivityAsDisplayed.mockResolvedValueOnce(true);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(0);
      expect(mutate.mock.calls).toHaveLength(0);
      const id = 10;
      await undoRequiredActionActivityDismissal(id);
      expect(activityHelpers.setActivityAsDisplayed.mock.calls).toHaveLength(1);
      expect(mutate.mock.calls).toHaveLength(1);
      expect(mutate.mock.calls[0][0]).toEqual("/api/user/required-activities/");
    });
  });
});
