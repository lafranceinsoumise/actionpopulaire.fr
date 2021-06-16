import React from "react";

import EventDescription from "./EventDescription";

const htmlDummyText =
  "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod" +
  "tempor incididunt ut labore et dolore magna aliqua. Euismod lacinia at" +
  'quis risus sed vulputate. <a href="#">Lobortis scelerisque</a> fermentum dui faucibus ' +
  "ornare quam. Dictum non consectetur a erat nam at. At ultrices mi " +
  "imperdiet nulla. Nulla pellentesque dignissim enim sit amet. Sagittis" +
  "aliquam malesuada bibendum arcu vitae elementum curabitur. Dictum fusce" +
  "ut placerat orci nulla pellentesque dignissim. Volutpat consequat " +
  "nunc congue nisi vitae suscipit tellus. Eget est lorem ipsum dolor" +
  "Aliquet enim tortor at auctor urna nunc id cursus metus.</p>" +
  "<p>Sit amet nisl purus in. In massa tempor nec feugiat nisl pretium. " +
  "tempor nec feugiat nisl pretium fusce id. Varius morbi enim nunc " +
  "a pellentesque sit amet. In hac habitasse platea dictumst quisque. Lorem" +
  "ipsum dolor sit amet consectetur adipiscing elit pellentesque. " +
  "pretium quam vulputate dignissim suspendisse in est ante. At " +
  "pellentesque adipiscing commodo elit. Lacinia quis vel eros donec" +
  "Facilisi nullam vehicula ipsum a. Montes nascetur ridiculus mus " +
  "vitae ultricies. Praesent elementum facilisis leo vel fringilla. Arcu" +
  "bibndum at varius vel pharetra vel turpis. Pretium aenean pharetra magna.</p>";

export default {
  component: EventDescription,
  title: "Events/Description",
};

const Template = (args) => <EventDescription {...args} />;

export const Default = Template.bind({});
Default.args = {
  compteRendu: htmlDummyText,
  compteRenduPhotos: [
    {
      thumbnail: "https://picsum.photos/200/200",
      image: "https://picsum.photos/200/200",
    },
    {
      thumbnail: "https://picsum.photos/200/200",
      image: "https://picsum.photos/200/200",
    },
  ],
  illustration: {
    thumbnail:
      "https://i.picsum.photos/id/523/1920/1080.jpg?hmac=sy_3fHrsxYu8cmYYWmQ2yWzPMfGNI42qloxWKF97ISk",
    banner:
      "https://i.picsum.photos/id/523/1920/1080.jpg?hmac=sy_3fHrsxYu8cmYYWmQ2yWzPMfGNI42qloxWKF97ISk",
  },
  description: htmlDummyText,
};
