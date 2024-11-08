import React from 'react';

const ActionProvider = ({ createChatBotMessage, setState, children }) => {
	// const handleHello = () => {
	//   const botMessage = createChatBotMessage('Hello. Nice to meet you.');

	//   setState((prev) => ({
	//     ...prev,
	//     messages: [...prev.messages, botMessage],
	//   }));
	// };

	const ask_date = (state) => {
		const botMessage = createChatBotMessage('Please provide the '+state);
		setState((prev) => ({
			...prev,
			messages: [...prev.messages, botMessage],
		}));
	};
	

	// Put the handleHello function in the actions object to pass to the MessageParser
	return (
		<div>
			{React.Children.map(children, (child) => {
				return React.cloneElement(child, {
					actions: {
						ask_date,
					},
				});
			})}
		</div>
	);
};

export default ActionProvider;