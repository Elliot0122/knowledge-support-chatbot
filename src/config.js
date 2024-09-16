import { createChatBotMessage } from 'react-chatbot-kit';

const config = {
  initialMessages: [createChatBotMessage(`Which type of panel would you like to include in your dashboard? For example, time series panel, map panel, and phylogenetic tree panel`)],
};

export default config;