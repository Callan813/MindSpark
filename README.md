# Mindspark

MindSpark is a powerful web-based AI writing assistant built with the MERN stack (MongoDB, Express.js, React, Node.js). It empowers users to generate, organize, and save AI-generated content for various use cases, such as blogging, creative writing, and ideation, using OpenAI's GPT-3.5-turbo model.

Features
AI-Powered Text Generation
Leverages OpenAI API to generate coherent and creative responses to user prompts.

Save & Manage Responses
Users can save generated responses for future reference or inspiration.

Clear Chat Functionality
Start fresh conversations anytime by clearing the chat.

History Log
Keep track of your past prompts and responses.

Tech Stack
Frontend: React.js, Tailwind CSS

Backend: Node.js, Express.js

Database: MongoDB

AI Engine: OpenAI (GPT-3.5-turbo)

State Management: React Hooks

Auth & Routing: React Router DOM

Installation
Prerequisites
Node.js & npm

MongoDB (local or Atlas)

OpenAI API Key

Clone the Repository
git clone https://github.com/Callan813/MindSpark.git
cd MindSpark

Backend Setup
cd server
npm install

Create a .env file in the server/ folder and add:
PORT=5000
MONGODB_URI=your_mongo_connection_string
OPENAI_API_KEY=your_openai_api_key

Frontend Setup
cd client
npm install
npm start

The frontend should now be running on http://localhost:3000 and the backend on http://localhost:5000.

Usage
Enter a prompt in the text field.

Click Generate to get AI-generated text.

Optionally, save the response to your history.

Use Clear Chat to start over.

Project Structure
bash
Copy
Edit
MindSpark/
├── client/        # React frontend
├── server/        # Express backend
├── README.md


Acknowledgements
OpenAI

MongoDB

React

Express

Contact
Developed by @Callan813 and @annjogeorge

