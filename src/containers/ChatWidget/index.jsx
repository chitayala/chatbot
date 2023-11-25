import { useState } from "react";
import { Paper, Box, Typography } from "@mui/material";
import { v4 as uuidv4 } from "uuid";
import { Link } from "react-router-dom";
import Header from "./ChatWidgetHeader";
import Body from "./ChatWidgetBody";
import Footer from "./ChatWidgetFooter";

//React Query Hook import
import { useSendUserMessage } from "../../hooks/mutations";

const initialChatWindowState = [
  {
    sender: "BOT",
    message: "What brings you here today?",
    messageId: uuidv4(),
  },
];

export default function ChatWidget({ businessId }) {
  const [chatWindowMessages, setChatWindowMessages] = useState(
    initialChatWindowState
  );

  const { mutateAsync: sendUserMessageToBot, isLoading } = useSendUserMessage();

  const onSendUserMessage = async (message) => {
    const newUserMessage = {
      sender: "USER",
      message,
      messageId: uuidv4(),
    };
    setChatWindowMessages((previousMessages) => [
      ...previousMessages,
      newUserMessage,
    ]);

    try {
      const userMessagePayload = {
        question: message,
        keywords: [],
        businessId,
      };
      await sendUserMessageToBot(userMessagePayload, {
        onSuccess: (data) => {
          if (data?.status && data.status === 200) {
            const newBotMessage = {
              sender: "BOT",
              message: data.answer,
              messageId: uuidv4(),
            };
            setChatWindowMessages((previousMessages) => [
              ...previousMessages,
              newBotMessage,
            ]);
          } else {
            const newBotMessage = {
              sender: "BOT",
              message: "Bot is not responding. Please try again",
              messageId: uuidv4(),
            };
            setChatWindowMessages((previousMessages) => [
              ...previousMessages,
              newBotMessage,
            ]);
          }
        },
        onError: () => {
          const newBotMessage = {
            sender: "BOT",
            message: "Bot is not responding. Please try again",
            messageId: uuidv4(),
          };
          setChatWindowMessages((previousMessages) => [
            ...previousMessages,
            newBotMessage,
          ]);
        },
      });
    } catch (error) {
      console.log("error in sending message to bot", error);
    }
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center",   height: "90vh",  maxHeight: "140vh" }}>
      {/* <iframe
        style={{ height: "99vh", width: "100vw", border: "unset" }}
        id="userWebsite-iFrame"
      /> */}
      <Typography variant="h6" style={{ margin: "30px" }}>
        Automated Assistant for Bank FAQ
      </Typography>
      <Paper className="paper-class"
        sx={{
          width: "400px",
          position: "fixed",
          right: "3rem",
          boxShadow: "0 4px 20px 0 hsl(0deg 0% 7% / 20%)",
          '@media only screen and (max-width: 1440px)' : {
            top: "6rem",
          },
          '@media screen  and (min-device-width: 1920px)': { 
            top: "15rem !important",
          }
        }}
      >
        <Header />
        <Body chatWindowMessages={chatWindowMessages} isLoading={isLoading} />
        <Footer sendMessage={onSendUserMessage} />
      </Paper>
    </Box>
//     <Box
//   sx={{
//     display: "flex",
//     justifyContent: "center",
//     alignItems: "flex-end",
//     minHeight: "87vh",
//     height: "95vh", 
//     maxHeight: "140vh"
//   }}
// >
//   <Box
//     sx={{
//       width: "100%",  // Make the container full width
//       maxWidth: "1200px",  // Add a maximum width to limit its size on large screens
//       display: "flex",
//       flexDirection: "column",
//       alignItems: "left",
//     }}
//   >
//     <Typography variant="h6" style={{ margin: "30px" }}>
//       Automated Assistant for Bank FAQ
//     </Typography>
//     <Paper
//       sx={{
//         width: "100%",  // Make the paper element full width
//         maxWidth: "400px",  // Set a maximum width for the paper
//         boxShadow: "0 4px 20px 0 hsl(0deg 0% 7% / 20%)",
//       }}
//     >
//       <Header />
//       <Body chatWindowMessages={chatWindowMessages} isLoading={isLoading} />
//       <Footer sendMessage={onSendUserMessage} />
//     </Paper>
//   </Box>
// </Box>

  );
}
