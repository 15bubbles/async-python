### TODO

- read urls from file
- add exception handling
- solve weird Windows' proactor event loop problem
- add some CLI
- some better logic that limits number of active coroutines (however adds coroutines when slots are available), because at the moment it gathers some number of coroutines and waits for all of them to finish until it will take another chunk of urls