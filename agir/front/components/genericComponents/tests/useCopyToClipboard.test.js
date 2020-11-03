import { renderHook, act } from "@testing-library/react-hooks";

import useCopyToClipboard from "../useCopyToClipboard";

describe("useCopyToClipboard", function () {
  beforeAll(function () {
    jest.spyOn(window, "setTimeout");
    jest.spyOn(console, "error");
    console.error.mockReturnValue();
    window.navigator.clipboard = {
      writeText: jest.fn().mockResolvedValue(),
    };
  });
  afterEach(function () {
    window.setTimeout.mockClear();
    window.navigator.clipboard.writeText.mockClear();
  });
  afterAll(function () {
    window.setTimeout.mockRestore();
    console.error.mockRestore;
    window.navigator.clipboard = undefined;
  });
  it("should return an array with a boolean and a function", function () {
    const args = ["text", 100];
    const { result } = renderHook(() => useCopyToClipboard(...args));
    expect(result.current).toBeInstanceOf(Array);
    expect(typeof result.current[0]).toBe("boolean");
    expect(typeof result.current[1]).toBe("function");
  });
  it("should return set isCopied to false by default", function () {
    const args = ["text", 100];
    const { result } = renderHook(() => useCopyToClipboard(...args));
    expect(result.current[0]).toBe(false);
  });
  it("should set isCopied to false if handleCopy is called and argument text is not a string", async function () {
    const args = [12345, 100];
    const { result } = renderHook(() => useCopyToClipboard(...args));
    expect(result.current[0]).toBe(false);
    expect(window.navigator.clipboard.writeText.mock.calls).toHaveLength(0);
    await act(async () => {
      result.current[1]();
    });
    expect(window.navigator.clipboard.writeText.mock.calls).toHaveLength(0);
    expect(result.current[0]).toBe(false);
  });
  it("should set isCopied to true if handleCopy is called and copy-to-clipboard succeeds", async function () {
    const args = ["text", 100];
    const { result } = renderHook(() => useCopyToClipboard(...args));
    expect(result.current[0]).toBe(false);
    expect(window.navigator.clipboard.writeText.mock.calls).toHaveLength(0);
    await act(async () => {
      result.current[1]();
    });
    expect(window.navigator.clipboard.writeText.mock.calls).toHaveLength(1);
    expect(result.current[0]).toBe(true);
  });
  it("should set isCopied to false if handleCopy is called and copy-to-clipboard fails", async function () {
    window.navigator.clipboard.writeText.mockRejectedValueOnce(
      new Error("Aye!")
    );
    const args = ["text", 100];
    const { result } = renderHook(() => useCopyToClipboard(...args));
    expect(result.current[0]).toBe(false);
    expect(window.navigator.clipboard.writeText.mock.calls).toHaveLength(0);
    await act(async () => {
      result.current[1]();
    });
    expect(window.navigator.clipboard.writeText.mock.calls).toHaveLength(1);
    expect(result.current[0]).toBe(false);
  });
});
