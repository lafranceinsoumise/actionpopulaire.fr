import React from "react";

import Steps from ".";
import StepBar from "./StepBar";

export default {
  component: StepBar,
  title: "Generic/Steps/StepBar",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <Steps type="bar" {...args}>
    <div>
      <h3>Arepas de choclo</h3>
      <p>
        Para muchos las arepas de choclo son las favoritas de la inmensa
        variedad de arepas que tenemos en Colombia, por el contraste ideal de
        dulce y salado en su composición. Recién salidas del fuego son un
        deleite para el comensal y combinan perfectamente con los huevos
        revueltos del desayuno, aunque me atrevo a asegurar que se disfrutan muy
        bien solas y a cualquier hora del día.
      </p>
      <p>
        La elaboración de las arepas de choclo viene desde antes de la época de
        la conquista, cuando los indios amasaban los granos tiernos de las
        mazorcas, que posteriormente ponían al fuego. Actualmente, esta clase de
        arepas hace parte de la alimentación de los habitantes de las regiones
        antioqueña y cundiboyacense.
      </p>
    </div>
    <div>
      <h4>Ingredientes</h4>
      <ul>
        <li>2 tazas de granos de maíz</li>
        <li>½ taza de leche</li>
        <li>1 taza de harina de maíz (la de hacer arepas)</li>
        <li>2 cucharadas de mantequilla</li>
        <li>¼ taza de panela rallada (o azúcar moreno)</li>
        <li>Sal al gusto (opcional)</li>
        <li>Queso blanco (En U.S.A. empleo el queso Cotija o queso fresco)</li>
      </ul>
    </div>
    <div>
      <h4>Receta</h4>
      <ol>
        <li>En la licuadora mezclar los granos de maíz y la leche.</li>
        <li>
          Pasar la mezcla a un recipiente y agregar la harina, la panela y la
          sal al gusto.
        </li>
        <li>Amasar y verificar la sazón.</li>
        <li>Armar bolitas y aplanarlas hasta formar las arepas.</li>
        <li>
          Calentarlas en una sartén antiadherente y dejarlas cocer hasta que
          doren por ambos lados.
        </li>
        <li>
          Un poco antes de sacarlas del fuego, cubrirlas con rodajas de queso
          blanco y dejarlo derretir.
        </li>
      </ol>
    </div>
  </Steps>
);

export const Default = Template.bind({});
Default.args = {
  title: "Arepas de choclo",
};

export const AsForm = Template.bind({});
AsForm.args = {
  ...Default.args,
  as: "form",
  title: "Arepas de choclo",
  onSubmit: (e) => {
    e.preventDefault();
    alert("Buen provecho!");
  },
};
