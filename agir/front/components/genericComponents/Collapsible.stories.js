import React from "react";

import Collapsible from "./Collapsible";

export default {
  component: Collapsible,
  title: "Generic/Collapsible",
};

const Template = (args) => (
  <div style={{ maxWidth: "80%", margin: "0 auto" }}>
    <Collapsible {...args} />
  </div>
);

export const WithChildren = Template.bind({});
WithChildren.args = {
  children: (
    <>
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Euismod lacinia at
        quis risus sed vulputate. <a href="#">Lobortis scelerisque</a> fermentum
        dui faucibus ornare quam. Dictum non consectetur a erat nam at. At
        ultrices mi imperdiet nulla. Nulla pellentesque dignissim enim sit amet.
        Sagittis aliquam malesuada bibendum arcu vitae elementum curabitur.
        Dictum fusce ut placerat orci nulla pellentesque dignissim. Volutpat
        consequat nunc congue nisi vitae suscipit tellus. Eget est lorem ipsum
        dolor Aliquet enim tortor at auctor urna nunc id cursus metus.
      </p>
      <p>
        Sit amet nisl purus in. In massa tempor nec feugiat nisl pretium. tempor
        nec feugiat nisl pretium fusce id. Varius morbi enim nunc a pellentesque
        sit amet. In hac habitasse platea dictumst quisque. Lorem ipsum dolor
        sit amet consectetur adipiscing elit pellentesque. pretium quam
        vulputate dignissim suspendisse in est ante. At pellentesque adipiscing
        commodo elit. Lacinia quis vel eros donec Facilisi nullam vehicula ipsum
        a. Montes nascetur ridiculus mus vitae ultricies. Praesent elementum
        facilisis leo vel fringilla. Arcu bibndum at varius vel pharetra vel
        turpis. Pretium aenean pharetra magna.
      </p>
    </>
  ),
};
export const WithHTML = Template.bind({});
WithHTML.args = {
  ...WithChildren.args,
  dangerouslySetInnerHTML: {
    __html:
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
      "bibndum at varius vel pharetra vel turpis. Pretium aenean pharetra magna.</p>",
  },
};
export const WithStyledHTML = Template.bind({});
WithStyledHTML.args = {
  ...WithChildren.args,
  dangerouslySetInnerHTML: {
    __html: `<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;"><strong>Retrouvez toutes les informations pour la soirée sur notre site : <a href="http://latouraineinsoumise.blogspot.com/2019/10/instrumentalisation-de-la-justice.html">http://latouraineinsoumise.blogspot.com/2019/10/instrumentalisation-de-la-justice.html</a> </strong></p>
<div class="AfficheLawFare" style="display: flex; width: 1263px; color: #363636; font-family: Roboto, sans-serif; font-size: 20px; background-color: #d0e0e3;">
<div class="divText" style="width: 884.094px;">
<p lang="fr-FR">Le&nbsp;<strong>13 décembre 2019 à 20h</strong>, nous vous convions à une soirée-débat intitulée « <em>Instrumentalisation de la justice, répression des opposants au capitalisme, instauration d’un régime autoritaire ?&nbsp;</em> ». Elle aura lieu à la salle de réunion de l’association Jeunesse et Habitat, située au 16 rue Bernard Palissy à Tours (au fond de la cour, au sous-sol). L’entrée est gratuite.</p>
<p lang="fr-FR">Nous diffuserons le documentaire « Lawfare. Le cas Mélenchon » coréalisé par Sophia Chikirou et Jean-Marie Vaude. Ce film retrace le contexte dans lequel a lieu le procès de la France Insoumise. Il élargit le propos sur la criminalisation des opposants politiques et l’instrumentalisation de la justice pour intimider et faire taire les contestataires de l’ordre établi, qu’il s’agisse en France de gilets jaunes, de syndicalistes, de militants et d’élus politiques.</p>
</div>
</div>
<p style="color: #363636; font-family: Roboto, sans-serif; font-size: 20px; background-color: #d0e0e3;" lang="fr-FR">Pour le débat, nous aurons le plaisir d’accueillir&nbsp;<strong>Antoine Léaument</strong>, ancien assistant parlementaire de Jean-Luc Mélenchon au Parlement européen.</p>
<p style="color: #363636; font-family: Roboto, sans-serif; font-size: 20px; background-color: #d0e0e3;" lang="fr-FR">Comme à notre habitude, nous terminerons la soirée par un pot de l’amitié.</p>
<p style="color: #363636; font-family: Roboto, sans-serif; font-size: 20px; background-color: #d0e0e3;" lang="fr-FR">En attendant, on peut bouquiner ! Nous vous conseillons la lecture du dernier ouvrage de Jean-Luc Mélenchon,&nbsp;<em><a style="background: transparent; text-decoration-line: none; color: #f43d3d;" href="https://melenchon.fr/2019/09/25/mon-livre-et-ainsi-de-suite/">Et ainsi de suite</a></em>. Et, pour une réflexion historique et philosophique, l’ouvrage&nbsp;<em><a style="background: transparent; text-decoration-line: none; color: #f43d3d;" href="https://journals.openedition.org/lectures/34108">La société ingouvernable. Une généalogie du libéralisme autoritaire</a></em>&nbsp;de Grégoire Chamayou est magistral.</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;"><a style="background: #d0e0e3; color: #f43d3d; font-family: Roboto, sans-serif; font-size: 20px;" name="more"></a></p>
<p style="color: #363636; font-family: Roboto, sans-serif; font-size: 20px; background-color: #d0e0e3;" lang="fr-FR">On peut aussi, si ce n’est déjà fait, signer la&nbsp;<a style="background: transparent; text-decoration-line: none; color: #f43d3d;" href="https://www.change.org/p/le-temps-des-proc%C3%A8s-politiques-doit-cesser">pétition en ligne</a>&nbsp;contre le&nbsp;<em>Lawfare</em>.</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">&nbsp;</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">&nbsp;</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">&nbsp;</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">Le&nbsp;<em style="box-sizing: border-box;">lawfare</em>&nbsp;est une tactique d’instrumentalisation de la justice à&nbsp;des fins politiques.</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">Dans le monde, des personnalités politiques, syndicalistes et des lanceur·ses d’alerte en sont les cibles. En France,&nbsp;<span style="box-sizing: border-box; font-weight: bold;">Jean-Luc Mélenchon et La France insoumise vivent depuis un an les étapes d’un processus de décrédibilisation que ce documentaire décrypte.</span></p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">Tous les ingrédients d’une opération de&nbsp;<em style="box-sizing: border-box;">lawfare&nbsp;</em>sont présents&nbsp;: accusations sans preuve, justice d’exception, violation des droits et libertés, dénigrement médiatique.&nbsp;<span style="box-sizing: border-box; font-weight: bold;">La seule réponse possible&nbsp;: la mobilisation populaire.</span></p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">Samuel Gontier, journaliste, Régis de Castelnau, avocat, Guillaume Long, ancien ministre équatorien, Alexandre Langlois, policier, Gaël Quirante, syndicaliste, et d’autres expert·es apportent leur témoignage au long de ce film. Avec la participation de Jean-Luc Mélenchon.</p>
<p style="box-sizing: border-box; margin: 0px 0px 11px; color: #333333; font-family: 'Roboto Slab', serif; font-size: 16px;">Le&nbsp;<em style="box-sizing: border-box;">lawfare</em>&nbsp;cible des syndicalistes, des décrocheur·ses de portraits de Macron, des Gilets jaunes, des lanceur·ses d’alerte. Il n’y a pas un « cas Mélenchon » isolé mais une dérive qui touche tous les opposant·es.</p>pre`,
  },
};

export const WithFadingOverflow = Template.bind({});
WithFadingOverflow.args = {
  ...WithChildren.args,
  fadingOverflow: true,
};
