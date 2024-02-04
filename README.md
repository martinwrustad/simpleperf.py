README FOR SIMPLEPERF.PY // PORTOFOLIO 1 - S364582

** INFO FOR RUNNING PROGRAM **

- To run this simpleperf-program, tabulate needs to be installed.

- Program runs with " phyton3 simpleperf.py " in the terminal
- User needs to add -s (server) or -c (client) to run in one of the following modes, else an error-message occurs

** SERVER-flags **
- -p or --port for choosing which port to run on, 8088 is default
- -b or --bind for choosing which IP-address to run on, 127.0.0.1 is default
- -f or --format for choosing which format the recieved bytes are shown in on output, 
has to choose either B, KB or MB, MB is default
- -P or --parallel for being able to open for more parallel connections, 
must insert in both server and client for more than 1, 1 is default

** CLIENT-flags **
- -p or --port for choosing which port to run on, 8088 is default
- -I or --serverip for choosing the servers IP-address, 127.0.0.1 is default
- -f or --format for choosing which format the sent bytes are shown in on output,
has to choose either B, KB or MB, MB is default
- -P or --parallel for being able to connect parallel connections, 
must insert in both server and client for more than 1, 1 is default
- -t or --time to choose the duration-time for sending bytes to server, 25 is default
- -i or --interval for printing output of transfer every x second
- -n or --num for choosing how much data to send, 
must be written as x amount, following B, KB or MB without spaceing between