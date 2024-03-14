# Industry track

## Tic-Tac-Toe Game

## About the project

Tic-tac-toe is a game where two players take turns to add a marker to a 3x3 grid. Whoever gets 3 of their markers in a line (horizontal, vertical or diagonal) wins the game.

An example of the grid, with one player using X and another O as the marker:

  <br>X O X
  <br>O X O
  <br>X O X

In the above example, the player with marker X would be the winner for getting 3 X's in a row diagonally. The game client itself looks like this:

<figure>
    <img src="assets/images/tictactoe.png"
         alt="tic-tac-toe" width="900" height="300">
    <figcaption>Example game</figcaption>
</figure>

This project uses a Python implementation of tic-tac-toe to demonstrate a client-server structure. Clients can connect to the server as authorised “players," which then take turns updating the server's data (game status). 
Only one tic-tac-toe game is ongoing on the server at any given time.




## Implemented components:

<!--
Detailed description of the system architecture (Application-specific system components):
- System must have at least three nodes (e.g, containers)
- Each node must have a role: client, server, peer, broker, etc.

Participating nodes must:
- Exchange information (messages): RPC, client-server, publish/subscribe, broadcast, streaming, etc.
- Log their behavior understandably: messages, events, actions, etc.

Nodes (or their roles) do not have to be identical
For example, one acts as server, broker, monitor / admin, etc.
Each node must be an independent entity and (partially) autonomous

Detailed descriptions of relevant principles covered in the course (architecture, processes, communication, naming, synchronization, consistency and replication, fault tolerance); irrelevant principles can be left out.

-->

The system consists of a server and multiple clients. There can be a maximum of 2 player clients active, but other clients can be connected as viewers to get updates on the game status.
- The server keeps track of the game status and updates the clients on the game status.
- The client can display the game statuses that the server sends to it, and when it's the player's turn to make a move, the client will relay the player's turn (selected grid position) to the server.
- The server keeps sending updates about the game to connected player/viewer clients until the client stops acknowledging the updates.




## Built with:
<!--
Detailed description of the system functionality and how to run the implementation ( note that there is a separate getting started section right below this so... )

- If you are familiar with a particular container technology, feel free to use it (Docker is not mandatory)
- Any programming language can be used, such as: Python, Java, JavaScript, ..
- Any communication protocol / Internet protocol suite can be used: HTTP(S), MQTT, AMQP, CoAP, ..
-->

- Python 12.3
- Pygame 2.5.2

Communication: 
- TCP

Database:
- SQLite




## Getting Started:
<!--
Instructions on setting up your project locally
-->

To start the project server to test it on your own computer, follow these steps:
1. download the project (if you downloaded it as a zip file, remember to unzip the files before continuing)
2. Run: 
```
python src/server/server.py [--host (host-ip) --port (host-port)]
```
More information you can run: 
```
python src/server/server.py --help
```
<mark>HOX!</mark> : The server will generate a database file named 'user.db' in case it is not already present.

When the server is running, you can start connecting to it with clients.
To start a client to join a game of tic-tac-toe, you don't have to download the project files again.

If you don't have pygame installed, run:
```
pip install pygame
```

Joining the game as a player:
1. Make sure you've followed the steps to start the game server first, otherwise, the client has nothing to connect to
2. Run
```
python src/client/client.py [--address (server-address) --port (server-port)]
```
More information you can run: 
```
python src/client/client.py --help
```



## Results of the tests:
<!--
Detailed description of the system evaluation
Evaluate your implementation using selected criteria, for example:
- Number of messages / lost messages, latencies, ...
- Request processing with different payloads, ..
- System throughput, ..


Design two evaluation scenarios that you compare with each other, for example:
- Small number / large number of messages
- Small payload / big payload

Collect numerical data of test cases:
- Collecting logs of container operations
- Conduct simple analysis for documentation purposes (e.g. plots or graphs)
-->



## Acknowledgments:
<!-- 
list resources you find helpful
-->

The original game logic for tic-tac-toe in python by krishkamani on github https://github.com/krishkamani/Tic-Tac-Toe-Game-In-Python/tree/master

Python multiplayer online game tutorial by Tech With Tim on YouTube https://www.youtube.com/playlist?list=PLzMcBGfZo4-kR7Rh-7JCVDN8lm3Utumvq

