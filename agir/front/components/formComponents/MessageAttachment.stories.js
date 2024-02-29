import React from "react";

import routes from "@agir/front/globalContext/nonReactRoutes.config";
import MessageAttachment from "./MessageAttachment";

export default {
  component: MessageAttachment,
  title: "Form/MessageAttachment",
  parameters: {
    layout: "padded",
  },
};

const Template = ({ name, file, ...args }) => {
  const [value, setValue] = React.useState({
    name,
    file,
  });

  const inputRef = React.useRef();

  const handleChange = React.useCallback((e) => {
    const file = e?.target?.files && e.target.files[e.target.files.length - 1];

    if (!file) {
      setValue(null);
      return;
    }

    setValue({
      name: file.name,
      file: URL.createObjectURL(file),
    });
  }, []);

  React.useEffect(() => {
    if (!value) {
      inputRef.current.value = null;
    }
  }, [value]);

  return (
    <>
      <MessageAttachment
        {...args}
        name={value?.name}
        file={value?.file}
        onDelete={args.hasDelete ? () => handleChange() : null}
      />
      <hr />
      <input type="file" onChange={handleChange} ref={inputRef} />
      <pre>
        Value:{" "}
        {value ? (
          <strong>{JSON.stringify(value, null, "\r  ")}</strong>
        ) : (
          <em>empty</em>
        )}
      </pre>
    </>
  );
};

export const File = Template.bind({});
File.args = {
  name: "document.pdf",
  file: routes.livretAnimateurice,
  small: false,
  thumbnail: false,
  hasDelete: true,
};

export const SmallFile = Template.bind({});
SmallFile.args = {
  ...File.args,
  small: true,
};

export const ThumbnailFile = Template.bind({});
ThumbnailFile.args = {
  ...File.args,
  thumbnail: true,
};

export const Image = Template.bind({});
Image.args = {
  name: "image.jpg",
  file: "https://placekitten.com/640/360",
  small: false,
  thumbnail: false,
  hasDelete: true,
};

export const ThumbnailImage = Template.bind({});
ThumbnailImage.args = {
  ...Image.args,
  thumbnail: true,
};
