import React, { useState, useCallback } from "react";

import TextField from "./TextField";
import EmojiPicker from "./EmojiPicker";

export default {
  component: EmojiPicker,
  title: "Form/EmojiPicker",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = useState("");
  const handleChange = useCallback((e) => {
    setValue(e.target.value);
  }, []);
  const handleSelect = useCallback((emoji) => {
    setValue((state) => state + emoji);
  }, []);

  return (
    <div
      style={{
        boxSizing: "border-box",
        padding: "32px 16px",
        maxWidth: "480px",
        margin: "0 auto",
      }}
    >
      <TextField
        label="Texte avec emojis"
        value={value}
        onChange={handleChange}
      />
      <div style={{ textAlign: "right" }}>
        <EmojiPicker {...args} onSelect={handleSelect} />
      </div>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {};
