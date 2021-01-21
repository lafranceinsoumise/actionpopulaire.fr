import React from "react";

import MessageCard from "./MessageCard";

export default {
  component: MessageCard,
  title: "Generic/MessageCard",
  decorators: [
    (story) => (
      <div
        style={{
          maxWidth: 700,
        }}
      >
        {story()}
      </div>
    ),
  ],
};

const Template = (args) => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [comments, setComments] = React.useState(args.comments);
  const handleDelete = React.useCallback(async (message) => {
    setIsLoading(true);
    await new Promise((resolve) => {
      setTimeout(() => {
        setComments((state) => state.filter((m) => m.id !== message.id));
        setIsLoading(false);
        resolve();
      }, 2000);
    });
  }, []);
  const handleComment = React.useCallback(
    async (messageContent) => {
      setIsLoading(true);
      await new Promise((resolve) => {
        setTimeout(() => {
          setComments((state) => [
            ...state,
            {
              content: messageContent,
              author: args.user,
              id: String(Date.now()),
              created: new Date().toUTCString(),
            },
          ]);
          setIsLoading(false);
          resolve();
        }, 2000);
      });
    },
    [args.user]
  );
  return (
    <MessageCard
      {...args}
      onDelete={handleDelete}
      onComment={handleComment}
      comments={comments}
      isLoading={isLoading}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  user: {
    id: "Bill",
    fullName: "Bill Murray",
    avatar: "https://www.fillmurray.com/200/200",
  },
  messageURL: "#message",
  message: {
    id: "message",
    created: "2021-01-09 12:00:00",
    author: {
      id: "Bill",
      fullName: "Bill Murray",
      avatar: "https://www.fillmurray.com/200/200",
    },
    content:
      "Bonjour à tous les nouveaux membres ! Pour que tout le monde puisse vous connaître, je vous propose qu’on se rejoigne ensemble sur Zoom vendredi vers 20h.\n\nEst-ce que l’horaire convient à tout le monde ?",
    linkedEvent: {
      id: "12343432423",
      name: "Cortège France insoumise à la marche contre la fourrure 2020",
      rsvp: "CO",
      startTime: "2021-01-15 12:00:00",
      endTime: "2021-01-15 15:00:00",
      duration: 2,
      locationName: "Place de la République",
      locationAddress: "Place de la République\n75011 Paris",
      shortLocation: "Place de la République, 75011, Paris",
      routes: {
        join: "#join",
        cancel: "#cancel",
        compteRendu: "#compteRendu",
        details: "#details",
      },
      groups: [{ id: "A", name: "Groupe d'action 1" }],
    },
  },
  commentCount: 2,
  comments: [
    {
      id: "comment-1",
      author: {
        id: "Isabelle",
        fullName: "Isabelle Guérini",
      },
      content:
        "Est-ce que c’est possible de commencer un peu plus tard ? Ma fille termine le karaté et j’arriverai à la maison tout juste...",
      created: "2021-01-09 12:30:00",
    },
    {
      id: "comment-2",
      author: {
        id: "Isabelle",
        fullName: "Isabelle Guérini",
      },
      content:
        "Est-ce que c’est possible de commencer un peu plus tard ? Ma fille termine le karaté et j’arriverai à la maison tout juste...",
      created: "2021-01-09 12:30:00",
    },
  ],
};

export const NoComments = Template.bind({});
NoComments.args = {
  ...Default.args,
  comments: [],
  commentCount: 0,
};

export const NoEvent = Template.bind({});
NoEvent.args = {
  ...NoComments.args,
  message: {
    ...NoComments.args.message,
    linkedEvent: null,
  },
};
