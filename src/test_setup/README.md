## Testing system performance with Docker

Setup to test the performance in terms of time delay of the moves showing up for the players and for the viewers.

In these introductions, the tic-tac-toe server and the player clients are ran locally and the viewer clients in containers to easily keep the GUI for the players yet being able to scale the amount of the viewers easily.

In test_setup/client.py set the SERVER_ADDRESS variable to your local IP address.

First to build the image for viewer clients, use command:

```console
docker build -t tictactoe_client .
```

in this folder or replace '.' with the path to test_setup.

Then to use Docker volume to index and extract the logs from the clients, create a volume:

```console
docker volume create tictactoe_volume
```

From the volume, the logs can be obtained, and there is the 'config.txt' file which can be modified to set the starting index of the logs, e.g., if the content of config.txt is 1, the next log files will be client1.log, client2.log ...

Then to test the scalability/time performance, run the server locally, and then run command:

```console
docker service create --replicas 25 --name tictactoe_server --mount source=tictactoe_volume,target=/client tictactoe_client:latest
```

where replace 25 with the amount of replicas you want to use.
