import React from "react";

import Accordion from "./Accordion";

export default {
  component: Accordion,
  title: "Generic/Accordion",
};

const Template = () => {
  return (
    <div
      style={{
        margin: "20px auto",
        width: "100%",
        height: "80vh",
        maxWidth: "400px",
        boxShadow: "1px 1px 5px #DFDFDF",
      }}
    >
      <Accordion name="Nouveautés" icon="rss">
        <div style={{ width: "100%", padding: "1.5rem" }}>
          <strong style={{ margin: 0 }}>Nouveautés</strong>
          <p>
            But we’ve met before. That was a long time ago, I was a kid at St.
            Swithin’s.
          </p>
        </div>
        <Accordion name="Nouveautés (bis)" icon="repeat">
          <div style={{ width: "100%", padding: "1.5rem" }}>
            <strong style={{ margin: 0 }}>Nouveautés (bis)</strong>
            <p>
              But we’ve met before. That was a long time ago, I was a kid at St.
              Swithin’s.
            </p>
          </div>
        </Accordion>
      </Accordion>
      <Accordion name="Compte et sécurité" icon="lock">
        <div style={{ width: "100%", padding: "1.5rem" }}>
          <strong style={{ margin: 0 }}>Compte et sécurité</strong>
          <p>
            It used to be funded by the Wayne Foundation. It’s an orphanage. My
            mum died when I was small, it was a car accident. I don’t remember
            it. My dad got shot a couple of years later for a gambling debt. Oh
            I remember that one just fine. Not a lot of people know what it
            feels like to be angry in your bones. I mean they understand.
          </p>
        </div>
      </Accordion>
      <Accordion name="Les insoumis·es Pyrénées-Ménilmontant" icon="users">
        <div style={{ width: "100%", padding: "1.5rem" }}>
          <strong style={{ margin: 0 }}>
            Les insoumis·es Pyrénées-Ménilmontant
          </strong>
          <p>
            But we’ve met before. That was a long time ago, I was a kid at St.
            Swithin’s, It used to be funded by the Wayne Foundation. It’s an
            orphanage. My mum died when I was small, it was a car accident. I
            don’t remember it. My dad got shot a couple of years later for a
            gambling debt. Oh I remember that one just fine. Not a lot of people
            know what it feels like to be angry in your bones. I mean they
            understand. But we’ve met before. That was a long time ago, I was a
            kid at St. Swithin’s, It used to be funded by the Wayne Foundation.
            It’s an orphanage. My mum died when I was small, it was a car
            accident. I don’t remember it. My dad got shot a couple of years
            later for a gambling debt. Oh I remember that one just fine. Not a
            lot of people know what it feels like to be angry in your bones. I
            mean they understand.
          </p>
        </div>
      </Accordion>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {};
