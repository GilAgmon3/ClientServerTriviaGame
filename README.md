# Trivia Contest Client-Server Application

## Course Details
- **Course**: Introduction to Data Communications
- **Instructor**: Prof. Yossi Oren
- **Institution**: Ben-Gurion University, Israel

## Project Description
This project is a client-server application designed to implement a trivia contest game. 
Players participate in this game by answering true or false questions related to given facts as quickly as possible to score points.

## Objective
Our task is to develop both the client and the server components of the application. 
The trivia game should support multiple clients connecting to our server, all capable of receiving trivia questions, submitting answers, and receiving their scores.

## Trivia Topic
The current trivia topic is based on the "Friends" TV show.
However, the question set is designed to be modular, allowing for easy updates or changes to other topics if desired.

## Compatibility Requirement
All client and server applications must be fully compatible with each other, emphasizing the need for standardized data formats and communication protocols.

## How to Run the Applications
### Server
1. Navigate to the server directory.
2. Run `Server.py` to start the trivia server.
3. Each run of 'Server.py' creates a new server. You may create as much server as you want in the same time.


### Client
1. Navigate to the client directory.
2. Run `Client.py` to start the trivia client.
3. Each run of 'Client.py' creates a new client. You may create as much clients as you want in the same time.

## Development Environment
- Programming Language: Python 3.9
- External Libraries: `socket`, `json` (for data serialization)

## Contributors
- Tiltan Gilat
- Gil Agmon
