# imports necessary packages
import argparse
from tabulate import tabulate
from socket import *
import sys
import ipaddress
import threading
import time
import re

# creates a parser
parser = argparse.ArgumentParser(description="optional arguments", epilog="end of help")


# function for validating the port, argument val must be an integer between 1024 and 65535
def check_port(val):
    # checks if the value is null
    try:
        if val is not None:
            value = int(val)
        else:
            # sets port-number to 8088
            value = 8088
    except ValueError:
        # sends error-message if inserted value isnt an integer
        raise argparse.ArgumentTypeError('Expected an int-value. String-value was provided')
    # sends error-message if provided port-number isnt between 1024 and 65535
    if value < 1024 or value > 65535:
        raise argparse.ArgumentError("Port must be between 1024 and 65535")
    # returns port-numer if valid
    return value


# function for validating the time, must be an integer > 0
def check_time(val):
    # checks if provided duration-time is not null
    try:
        if val is not None:
            value = int(val)
        else:
            # sets duration time to 25
            value = 25
    except:
        # sends error-message if inserted value isnt an integer
        raise argparse.ArgumentTypeError('Expected int-value. String value was provided')
    if value < 1:
        # sens error-message if provided time is under 0 or lower
        raise argparse.ArgumentError("Must be over 0")
    # returns duration-time if valid
    return value


# function for changing format of bytes, uses the format and number of bytes as arguments
def check_format(form, amount):
    # variable form converts to string and variable bytes_ converts to integer
    form = str(form)
    bytes_ = int(amount)
    # returns the same amount if format B is provided
    if form == "B":
        bytes_ = bytes_
    # converts bytes to KB by dividing amount of bytes by 1000 if format KB is provided
    elif form == 'KB':
        bytes_ = bytes_ / 1000
    # converts bytes to MB by dividing by 1_000_000 if format MB is provided
    elif form == "MB":
        bytes_ = bytes_ / 1000000
    # returns right of bytes
    return int(bytes_)


# funtion for validating ip-adresses
def check_ip(val):
    # variable address is the provided argument val converted to string
    address = str(val)
    try:
        # uses the imported ipaddress-check to validate the provided address
        ipaddress.ip_address(address)
    except ValueError:
        # returns error-message of address isnt valid
        print(f"The ip-address {address} is not valid")
    # returns address if valid
    return address


# function for converting and splitting the -num flag. Code found in the help-slides on canvas
def check_size(val):
    # variable match uses re.match to validate provided input
    match = re.match(r"([0-9]+)([a-z]+)", val, re.I)
    if match:
        # variable items groups the two splitted arguments
        items = match.groups()
        # returns items as a list consisting of two elements
        return items
    if not match:
        # returns error-message if inserted value isnt valid
        raise ValueError("Invalid size value: {}".format(val))

# function for handeling clients, uses format, connection and address as arguments
def client_handle(form, conn, addr):
    # varible start_time is being set to current time and variable recieved_bytes is being declared as 0
    start_time = time.time()
    recieved_bytes = 0

    # loops as long as no break occurs
    while True:
        # variable data declared as recieved data from client, recieves up to 1000 bytes
        data = conn.recv(1000)
        # breaks if data isnt recieved
        if not data:
            break

        # breaks if FINISH-message if recieved
        if "FINISH" in data.decode():
            break

        # adds amount of data(bytes) to the total in recieved_bytes
        recieved_bytes += len(data)

    # variable end_time gets current time as current time
    end_time = time.time()
    # variable dur is amount of seconds of the duration
    dur = end_time - start_time
    # sets variable dur as 1.0 if the duration if under 1 second
    if dur < 1:
        dur = 1.0

    # sends an ACK-message to the client to acknowledge to stop and closes the connection
    conn.send("ACK".encode())
    conn.close()

    # uses the function check_format()-function above to convert the recieved amount of bytes to the chosen format
    recvbytes = check_format(form, recieved_bytes)
    # variable rate_bits converts number of bytes to bits by multiplying by 8,
    # divides by duration time and 1000000 to convert to MB/s
    rate_bits = recieved_bytes * 8 / dur / 1_000_000

    #creates strings for the printing

    # variable ipport is clients ip-address and portnumber
    ipport = str(addr[0])
    ipport += ':'
    ipport += str(addr[1])

    # variable duration is 0.0 - number of seconds of the duration
    duration = '0.0-'
    duration += str(round(dur, 1))

    # variable recv is amount of recieved bytes rounded down + format
    recv = str(round(recvbytes))
    recv += form

    # variable band is the rate of bits revieved with 2 desimals + Mbps
    band = str(round(rate_bits, 2))
    band += 'Mbps'

    #prints the results in a tabulate-table
    datas = [[ipport, duration, recv, band]]
    print(tabulate(datas, headers=['ID', 'INTERVAL', 'RECIEVED', 'RATE']))

# function for the server
def server():
    # creates the server socket and adresses the server port and ip-address
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverport = port
    server_address = ip

    # tries to bind the port to the ip and starts listening to connections
    try:
        serverSocket.bind((server_address, serverport))
        serverSocket.listen()
        # prints that the server is listening to connections on set portnr
        print("------------------------------------------------------")
        print("A simpleperf server is listening on port", serverport)
        print("------------------------------------------------------")
    except:
        # prints that bind was unsuccessful if ipaddress cant bind with portnr and exits
        print("Bind unseccessful, try again later")
        sys.exit()

    # created a variable threadcount which counts how many threads are being created
    threadcount = 0

    # loops as long as no break occurs
    while True:
        # saves clients connection and address when client connects to server socket
        conn, addr = serverSocket.accept()

        # server ip : port
        serviport = str(server_address)
        serviport += ':'
        serviport += str(serverport)

        # client ip-address : port
        cliport = str(addr[1])
        cliport += ":"
        cliport += str(serverport)

        # prints that client has connected to server on port and address
        print(f"\nA simpleperf client with {cliport} is connected with server {serviport} \n")

        # client_thread for every new thread, send new clients to client_handle with the arguments format,
        # connection and address
        client_thread = threading.Thread(target=client_handle, args=(form, conn, addr))
        # starts the thread
        client_thread.start()

        # adds 1 to the threadcount every time another thread has been created
        threadcount += 1

        # breaks out of the while-loop once the same amount of threads and chosen parallell connections have been created
        # important here that the -P flag is being used at both client and server-side with the same amount
        if threadcount == parallel:
            break


# function for clients
def client():
    # function threadcon() for operating with multiple parallell connections
    def threadcon():
        # one global and one nonlocal variable for handling different situations
        global form
        nonlocal successful_con

        # string for ip : port
        ipport = str(serverip)
        ipport += ':'
        ipport += str(port)

        # prints client connecting to server on set address and port
        print("---------------------------------------------------------------------")
        print(f"A simpleperf client connecting to server {serverip}, port {port}")
        print("---------------------------------------------------------------------")

        # tries to create a client socket and connect it to the server
        try:
            # clientsocket is the socket for client, uses AF_INTET and SOCK_STREAM as protocols values
            clientsocket = socket(AF_INET, SOCK_STREAM)
            # connects clientsocket to set address and portnumber
            clientsocket.connect((serverip, port))
            # saved current time on variable start_time
            start_time = time.time()
            # prints confirmation that a connection has been reached
            print(f"\nClient connected with {serverip} port {port}\n")
        except:
            # prints connection failed if connection didnt succeed
            print("Connection failed")

        # variable bytes_sent declared as 0
        bytes_sent = 0

        # if -num flag is being used
        if num:
            # numflag uses the check_size-function with provided input to split input to amount and format
            numflag = check_size(num)
            # numamount as the inserted amount
            numamount = int(numflag[0])
            # numform is the provided format
            numform = numflag[1]
            # sets the global variable form as provided format
            form = numform

            # converts amount of bytes to MB by multiplying by 1_000_000 if MB is provided in input
            if numform == "MB":
                numbytes = numamount * 1_000_000
            # converts amount of bytes to KB by multiplying by 1_000 if KB is provided in input
            elif numform == "KB":
                numbytes = numamount * 1000
            # if B is provided in input, numbytes is the same as numamount
            elif numform == "B":
                numbytes = numamount

            # loops as long as numbytes is larger than 1000
            while numbytes >= 1000:
                # variable is 1000 bytes
                data = bytes(1000)
                # sends 1000 bytes to the server
                clientsocket.sendall(data)
                # adds number of bytes sent to the total amount in bytes_sent
                bytes_sent += len(data)
                # subtracts 1000 bytes from numbytes as that has been sent
                numbytes -= 1000

            # if numbytes is under 1000, the rest is being sent at once and adds to the total
            if numbytes < 1000:
                rest = bytes(numbytes)
                clientsocket.sendall(rest)
                bytes_sent += len(rest)

        # if -interval flag is being used, prints results every (interval) second
        elif interval:
            # interval_starttime is the current time and interval_bytessent is 0
            interval_starttime = time.time()
            interval_bytessent = 0
            # prints the headers of the output
            print("{:<25} {:<10} {:<15} {:<10}".format('ID', 'INTERVAL', 'TRANSFER', 'BANDWIDTH'))

            # prints results every (interval)-second in for-loop
            for i in range(interval, interval + durtime, interval):
                # sends bytes as long as the interval runs
                while time.time() - interval_starttime < interval:
                    data = bytes(1000)
                    clientsocket.sendall(data)
                    interval_bytessent += len(data)
                    bytes_sent += len(data)

                # variable dur is the number of interval-seconds
                dur = interval

                # string transf is the output-string for bytes sent in each interval with 1 decimal + format
                transf = str(round(check_format(form, interval_bytessent), 1))
                transf += str(form)

                # bandwidth is number of bytes sent converted to bits divided by duration and 1_000_000
                bandwidth = interval_bytessent * 8 / dur / 1_000_000

                # prints the result of each interval consecutively
                print("{:<25} {:<10} {:<15} {:.2f} Mbps".format(ipport, "{:.1f}-{:.1f}".format(i - interval, i), transf, bandwidth))

                # resets variavles interval_bytessent and interval_starttime for next interval
                interval_bytessent = 0
                interval_starttime = time.time()

        # prints results after -t seconds if neither of interval or num-flags are being provided
        else:
            # sends bytes as long as the set duration lasts
            while time.time() - start_time < durtime:
                data = bytes(1000)
                clientsocket.sendall(data)
                bytes_sent += len(data)

        # sends FINISH to the server to stop sending data
        clientsocket.send('FINISH'.encode())

        # stops the time once recieved an ACK-message from the server and closes the connection
        while True:
            message = clientsocket.recv(1000)
            if 'ACK' in message.decode():
                break

        # stops the time in client_end_time after transfer is done
        client_end_time = time.time()

        # closes connection
        clientsocket.close()

        # sets dur to duration for total sending-time, and to 1 if the duration is below 1
        dur = client_end_time - start_time
        if dur < 1:
            dur = 1.0

        # creates strings for output
        bandwid = (bytes_sent / dur) * 8 / 1_000_000
        sentbytes = check_format(form, bytes_sent)
        intervalstr = '0.0-'
        intervalstr += str(round(dur, 1))
        transtr = str(round(sentbytes))
        transtr += str(form)
        bandstr = str(round(bandwid, 2))
        bandstr += 'Mbps'

        # prints the total summary of the transfer through a tabulate-table
        datas = [[ipport, intervalstr, transtr, bandstr]]
        print('-----------------------------------------------------------')
        print(tabulate(datas, headers=['ID', 'INTERVAL', 'TRANSFER', 'BANDWIDTH']))

    # array for threads
    threads = []

    # creates the specific number of parallel connections, one client for each parallel
    for i in range(parallel):
        # onetread is the same of the new thread for each parallel, gets sent to the threadcon-function
        onethread = threading.Thread(target=threadcon)
        # sleeps for 1 second for spreading the load
        time.sleep(1)
        # starts the new thread and adds it to the array
        onethread.start()
        threads.append(onethread)
    # declares successful_con as 0
    successful_con = 0
    # for each thread in array threads
    for thread in threads:
        # every thread joins in and successful_con increases by 1
        thread.join()
        successful_con += 1
    if successful_con == parallel:
        # prints all clients done when all clients are done transfering
        print("All clients done")


# main-function starts with program start
if __name__ == '__main__':

    # adds all arguments to the parser. -s and -c are boolean and are therefore 'store_true'
    parser.add_argument('-s', '--server', action='store_true', help='server or client')
    parser.add_argument('-c', '--client', action='store_true', help='server or client')

    # -p specifies what port to run on, -b is what ip-address the server runs on,
    # -f is chosen format (must choose between B, KB or MB), -I is what ip-address the client shall run on,
    # -t is the duration-time the client shall send data, -i is number of seconds each interval is,
    # -P is how many parallel connections shall be opened, -n is number of bytes shall be sent
    parser.add_argument('-p', '--port', type=check_port, default=8088, help='Port number for server')
    parser.add_argument('-b', '--bind', type=check_ip, default='127.0.0.1', help='IP-address for server')
    parser.add_argument('-f', '--format', type=str, choices=['B', 'KB', 'MB'], default='MB', help='format of the summary')
    parser.add_argument('-I', '--serverip', type=check_ip, default='127.0.0.1', help='servers ip-address')
    parser.add_argument('-t', '--time', type=check_time, default=25, help='time of duration in seconds')
    parser.add_argument('-i', '--interval', type=int, help='statistics per second')
    parser.add_argument('-P', '--parallel', type=int, default=1, help='number of parallel connections')
    parser.add_argument('-n', '--num', type=str, help='amount of bytes in either B, KB or MB')

    # args parses the parsers arguments
    args = parser.parse_args()

    # creates variables for the flags
    port = args.port
    ip = args.bind
    form = args.format
    serverip = args.serverip
    durtime = args.time
    interval = args.interval
    parallel = args.parallel
    num = args.num

    # sends to user to the chosen destination. Not possible to run in both client and server or none
    if args.server and args.client:
        print("You can only run one of client and server!")
    elif args.server:
        server()
    elif args.client:
        client()
    else:
        print("ERROR: YOU MUST RUN IN EITHER SERVER OR CLIENT MODE")
