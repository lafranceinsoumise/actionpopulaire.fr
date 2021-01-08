import React from "react";

import BottomSheet from "./BottomSheet";

export default {
  component: BottomSheet,
  title: "Generic/BottomSheet",
};

export const Default = (props) => {
  const [isOpen, setIsOpen] = React.useState(true);
  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <div
      onClick={isOpen ? undefined : handleOpen}
      style={{
        background: "dodgerblue",
        width: "100vw",
        height: "100vh",
        cursor: isOpen ? "default" : "pointer",
      }}
    >
      <BottomSheet {...props} isOpen={isOpen} onDismiss={handleDismiss}>
        <pre style={{ border: "1px dashed dodgerblue", textAlign: "center" }}>
          I am the BottomSheet content !
        </pre>
      </BottomSheet>
    </div>
  );
};

export const LongContent = (props) => {
  const [isOpen, setIsOpen] = React.useState(true);
  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <div
      onClick={isOpen ? undefined : handleOpen}
      style={{
        background: "dodgerblue",
        width: "100vw",
        height: "100vh",
        cursor: isOpen ? "default" : "pointer",
      }}
    >
      <BottomSheet {...props} isOpen={isOpen} onDismiss={handleDismiss}>
        <div style={{ fontSize: "14px", padding: "1rem 2rem" }}>
          <p>
            Cupcake ipsum dolor sit. Amet soufflé powder. Cake bear claw lemon
            drops cupcake gummi bears candy canes. Apple pie pie chupa chups
            marzipan soufflé sugar plum biscuit sesame snaps. Bonbon dragée
            donut dessert. Cotton candy lemon drops topping croissant. Pie
            dragée carrot cake pie marshmallow muffin jujubes danish. Dessert
            icing candy. Candy canes jelly dragée chocolate. Marzipan jelly-o
            croissant gummi bears pastry. Sugar plum topping cupcake tootsie
            roll cake. Soufflé candy canes lollipop topping muffin jelly beans
            dessert marshmallow. Carrot cake sweet roll I love I love soufflé
            oat cake pastry.
          </p>
          <p>
            Tootsie roll jelly sesame snaps. I love chocolate bar sugar plum
            cheesecake. Dessert jelly beans caramels candy marzipan pie donut.
            Biscuit jelly beans gummies candy jujubes jujubes jelly beans wafer
            brownie. Icing ice cream croissant biscuit cookie marzipan chupa
            chups icing. Candy brownie chupa chups I love donut icing tiramisu.
            Lollipop sesame snaps croissant I love carrot cake liquorice jelly.
            Cupcake I love powder. Bonbon danish bear claw icing chocolate bar
            liquorice caramels powder. Topping sweet bear claw marshmallow I
            love cake. Pie candy I love chupa chups bonbon chupa chups jelly
            beans I love jujubes. Jelly-o toffee tiramisu cake toffee oat cake.
          </p>
          <p>
            Toffee bonbon sugar plum danish. Gingerbread icing I love apple pie
            caramels cake lemon drops dragée. Lollipop sweet roll cheesecake
            pie. Sugar plum macaroon liquorice I love. Cotton candy wafer lemon
            drops gummi bears cheesecake bonbon gummi bears tootsie roll. Sesame
            snaps cake macaroon soufflé bear claw. Cupcake liquorice tootsie
            roll tiramisu pie chocolate chocolate cake. Cake lollipop cupcake
            jelly-o sweet. Marshmallow liquorice biscuit bear claw cookie cake.
            Gummies tart I love macaroon pie sweet marshmallow chocolate.
            Caramels carrot cake gummi bears biscuit soufflé. Candy canes
            cupcake cake.
          </p>
          <p>
            Croissant cake soufflé cake liquorice gummi bears carrot cake gummi
            bears wafer. Pastry chocolate bar jelly-o tiramisu dragée. Chocolate
            pastry tiramisu biscuit biscuit pudding cookie carrot cake ice
            cream. Jujubes tootsie roll brownie wafer. Lemon drops I love powder
            oat cake cake fruitcake I love. Fruitcake pudding wafer pudding bear
            claw carrot cake muffin bonbon chocolate cake. Tiramisu lollipop
            pudding chupa chups sweet dessert cupcake sweet roll chupa chups.
            Donut cake sesame snaps. Oat cake gummi bears bonbon I love. Topping
            I love chupa chups oat cake sugar plum chocolate cake chupa chups.
            Gummi bears gummi bears macaroon croissant donut donut caramels
            cake. Cookie caramels gummies cupcake wafer fruitcake liquorice
            brownie. Gummi bears biscuit danish liquorice sweet roll chupa chups
            bonbon. Brownie I love lollipop tart I love fruitcake pie I love.
          </p>
          <p>
            Lollipop cake I love topping carrot cake lollipop. Apple pie jelly-o
            carrot cake marzipan lemon drops I love toffee tootsie roll. Powder
            liquorice halvah apple pie. Cupcake powder jujubes I love
            gingerbread I love. Biscuit jelly beans caramels. Pie tiramisu jelly
            beans carrot cake croissant tootsie roll danish. I love bear claw
            toffee. Cake cake muffin cheesecake chocolate cake sugar plum bonbon
            tootsie roll. Cheesecake biscuit I love wafer I love cheesecake
            cotton candy lemon drops cake. Sweet roll biscuit tootsie roll
            tootsie roll cotton candy icing tart. Bear claw lemon drops jelly
            beans. Chocolate cake cupcake sweet roll donut chupa chups danish
            chupa chups tootsie roll. Macaroon jelly ice cream powder chupa
            chups carrot cake I love liquorice. Bear claw tiramisu candy canes
            cupcake.
          </p>
          <p>
            Chocolate cake I love croissant tart marshmallow sugar plum
            marshmallow. Lemon drops jujubes powder sweet. Toffee brownie sugar
            plum jujubes chupa chups muffin lemon drops pie cupcake. Biscuit
            sugar plum carrot cake. Croissant candy canes apple pie. Muffin
            soufflé chupa chups I love. Caramels donut marzipan jelly candy.
            Cake topping oat cake cake. Cheesecake powder I love sweet.
            Fruitcake lemon drops I love fruitcake jelly beans cake. Powder
            jelly beans chocolate cake bear claw chocolate cake carrot cake ice
            cream. Gingerbread bonbon oat cake tart. Cheesecake ice cream donut
            sugar plum chupa chups candy canes sweet roll croissant cookie.
            Gummies gummi bears jelly.
          </p>
          <p>
            Jujubes I love toffee croissant lollipop icing bear claw cotton
            candy biscuit. Lemon drops macaroon ice cream marzipan. Bear claw
            macaroon brownie chocolate cake marshmallow I love. Tart halvah
            croissant liquorice halvah I love toffee. I love bonbon biscuit
            dessert cupcake. Jujubes dragée tiramisu ice cream apple pie
            marzipan. Marshmallow muffin caramels gummies cupcake fruitcake
            cake. Lemon drops sugar plum macaroon tiramisu caramels powder
            marzipan carrot cake marshmallow. Jelly lemon drops caramels jelly-o
            cake gingerbread toffee. Marzipan topping donut jelly-o chocolate
            cake jujubes fruitcake. Pie jelly beans fruitcake halvah liquorice
            soufflé pastry. Tart sugar plum lollipop chocolate bonbon halvah
            chocolate cake. Icing tootsie roll I love brownie powder jelly
            cheesecake I love lollipop.
          </p>
          <p>
            Carrot cake bear claw icing oat cake I love. Jelly I love sweet
            liquorice gingerbread. Lemon drops I love gingerbread gummies. I
            love soufflé jelly sweet bonbon sweet roll jelly. Ice cream sugar
            plum halvah cookie lemon drops. Sugar plum ice cream jelly I love
            gingerbread gingerbread I love. Candy canes candy marzipan gummies.
            I love dessert carrot cake sesame snaps oat cake marzipan
            marshmallow chupa chups lollipop. Topping oat cake sesame snaps I
            love danish topping. Jelly-o oat cake halvah caramels pastry.
            Brownie cheesecake I love. Ice cream chocolate bar cheesecake. Oat
            cake gummies soufflé bear claw cupcake. Cookie pudding halvah sugar
            plum carrot cake caramels.
          </p>
          <p>
            Pastry powder chocolate cake icing I love dessert topping. Bonbon
            candy canes oat cake cupcake candy canes croissant. Cookie lemon
            drops soufflé. Cake candy canes lollipop cookie chocolate sesame
            snaps marshmallow. Caramels danish cake. Candy sweet roll brownie
            jelly beans pudding. I love fruitcake icing brownie. Chocolate bar
            icing I love apple pie soufflé croissant chocolate cake muffin.
            Sugar plum lollipop cheesecake. Wafer halvah chocolate carrot cake
            tootsie roll cheesecake I love. Chocolate cake halvah bear claw
            sugar plum apple pie chocolate. Cake soufflé candy canes powder I
            love croissant jelly-o. Gingerbread I love chocolate bar tart
            tootsie roll caramels I love. Donut danish oat cake.
          </p>
          <p>
            I love I love caramels. Icing bear claw I love. Bear claw gummies
            halvah bonbon jelly gummi bears candy chupa chups. Tart tart sweet
            halvah gummi bears marshmallow donut tiramisu. Candy marzipan sugar
            plum. Croissant candy canes jujubes pastry powder muffin fruitcake I
            love. Candy cake ice cream caramels. Cotton candy cake cupcake. I
            love topping cookie fruitcake macaroon donut bear claw dragée cake.
            I love marzipan gummi bears lollipop toffee sesame snaps. Cake cake
            cheesecake I love powder toffee. Donut chocolate cake lollipop jelly
            beans gummi bears tiramisu tart pastry candy canes.
          </p>
          <p>
            Chupa chups fruitcake marshmallow I love gingerbread jelly macaroon
            wafer sesame snaps. Pie caramels chocolate cake jujubes lollipop
            halvah. Ice cream macaroon candy donut fruitcake. Croissant I love
            cake sweet roll. Cake cookie cake bonbon I love gummies. Chocolate
            gummi bears carrot cake biscuit fruitcake carrot cake jelly-o
            biscuit chocolate cake. Halvah lollipop chupa chups chupa chups
            sweet roll. Lemon drops jelly beans jelly beans. Chupa chups
            croissant caramels marzipan oat cake chocolate bar. Gummi bears
            cotton candy cotton candy chocolate bar halvah oat cake muffin
            tiramisu. Lollipop sweet roll gingerbread cheesecake cupcake sweet
            roll ice cream bonbon. I love cheesecake cupcake.
          </p>
          <p>
            I love pie topping I love biscuit dessert chocolate bar jelly-o.
            Danish oat cake lollipop ice cream cake carrot cake liquorice
            pudding. I love topping oat cake topping. Candy canes pastry tart
            cookie. I love topping tart I love croissant. Jelly marzipan bonbon
            bonbon dessert pie jujubes. Bonbon chocolate sugar plum bonbon tart
            I love bonbon chupa chups sweet roll. Cake marshmallow dessert. Cake
            candy chupa chups donut. Dragée cake tiramisu biscuit jujubes
            gummies pie sugar plum. Muffin biscuit tart oat cake. Brownie
            marshmallow powder oat cake candy. Topping apple pie gummies
            jelly-o.
          </p>
          <p>
            Bear claw I love dessert. Gingerbread tiramisu candy chocolate cake
            soufflé muffin liquorice. Jelly-o fruitcake tootsie roll lollipop.
            Lemon drops fruitcake candy topping candy gingerbread. Donut sesame
            snaps caramels jelly chocolate. Gummi bears ice cream bonbon sugar
            plum. Ice cream lemon drops soufflé marzipan chocolate cake
            chocolate cake lollipop dragée. Icing brownie candy canes carrot
            cake cake icing fruitcake. Pastry pie halvah. Caramels halvah jelly
            halvah donut dessert sweet bear claw. Caramels biscuit gummi bears
            chocolate cake biscuit ice cream. I love I love jujubes macaroon
            brownie I love biscuit biscuit. I love dragée apple pie carrot cake
            macaroon sugar plum. Caramels donut icing wafer.
          </p>
          <p>
            I love lemon drops jelly-o pastry muffin I love. Jujubes brownie
            bonbon bonbon muffin lollipop I love. Biscuit dragée bonbon cotton
            candy dragée sweet roll tart. I love pudding cookie icing cotton
            candy gummi bears cake lollipop. Cupcake chupa chups bear claw.
            Biscuit cheesecake donut pie. Donut I love sesame snaps cotton
            candy. Marzipan jelly donut brownie soufflé. Cotton candy lemon
            drops sugar plum powder brownie sweet roll I love candy. Carrot cake
            oat cake caramels fruitcake I love bear claw. I love marzipan chupa
            chups cheesecake sesame snaps. Jelly candy cake sesame snaps toffee
            topping.
          </p>
          <p>
            Caramels jelly-o toffee soufflé marshmallow chupa chups sweet oat
            cake jelly-o. I love bear claw candy donut. Jelly beans fruitcake
            macaroon I love lollipop. I love dragée danish chocolate cake
            jujubes apple pie jujubes gummies. Donut danish candy caramels.
            Carrot cake bonbon halvah bear claw lemon drops cookie I love
            biscuit. Cheesecake chocolate cake chocolate pastry caramels jelly
            beans carrot cake fruitcake dragée. I love jujubes jelly beans
            topping apple pie pie pastry macaroon. Liquorice tart I love chupa
            chups pastry biscuit. Marshmallow tart chocolate bar I love halvah
            sweet roll. Cake chupa chups powder jelly beans toffee soufflé candy
            carrot cake. Chocolate lemon drops pie toffee. Cotton candy cookie
            candy canes cake pudding danish.
          </p>
        </div>
      </BottomSheet>
    </div>
  );
};
