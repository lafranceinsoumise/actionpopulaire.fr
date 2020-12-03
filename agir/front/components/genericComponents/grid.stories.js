import React from "react";
import Card from "./Card";
import { Column, Container, Row } from "./grid";

export default {
  title: "Generic/Grid",
};

const Template = () => (
  <Container style={{ border: "3px solid black" }}>
    <Row gutter={72} style={{ backgroundColor: "blue" }}>
      <Column grow style={{ border: "3px solid red" }}>
        <Card>
          <p>
            Ici on a un Container, avec une &lt;Row gutter={72}&gt; (en bleu).
          </p>
          <p>
            La première colonne a la propriété grow, la deuxième width="434px"
          </p>
        </Card>
        <Row gutter={12} style={{ backgroundColor: "yellow" }}>
          <Column width="50%">
            <Card>Une Row avec un gutter de 12 dans une colonne</Card>
          </Column>
          <Column width="50%">
            <Card>Ça marche</Card>
          </Column>
        </Row>
        <Card>
          Les Card ont elle même un padding, et une margin bottom de 10px
        </Card>
      </Column>
      <Column width="434px">
        <Card>Row est le seul item a prendre le paramètre gutter</Card>
      </Column>
    </Row>
    <Row gutter={22}>
      <Column width="33%">
        <Card>Ici chaque colonne a width="33%"</Card>
      </Column>{" "}
      <Column width="33%">
        <Card>Une ligne dans une colonne avec un plus petit gutter</Card>
      </Column>
      <Column width="33%">
        <Card>Ça marche</Card>
      </Column>
    </Row>
  </Container>
);

export const FixedSideBarExample = Template.bind({});
FixedSideBarExample.args = {
  stack: false,
};
