#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include "utils.h"

#define BUF_SIZE (100 * 1024) // set buffer size to 100 KB
#define BACKLOG 5             // maximum number of client connections allowed

// function to handle client communication
void handle_client(int client_socket) 
{
    char buffer[BUF_SIZE];
    int bytes_read;
    memset(buffer, 0, sizeof buffer);
    printf("Handling client communication on PID: %d\n", getpid());
    // read data from the client socket
    if ((bytes_read = read(client_socket, buffer, BUF_SIZE)) == -1) 
    {
        perror("Error reading stream message");
        exit(4); 
    }
    if (bytes_read == 0)
        printf("Ending connection\n");
    
    close(client_socket);
}

void main(int argc, char *argv[])
{
    int sock, length;                           // server socket file descriptor
    struct sockaddr_in server, client_addr;     // server and client address structures
    socklen_t client_len = sizeof(client_addr); // length of the client address structure
    int client_sock;                            // socket for client connection

    if (argc < 3)
    {
        perror("incorrect arguments");
        exit(4);
    }

    // create a TCP socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        perror("Error opening socket");
        exit(1);
    }
    if (inet_pton(AF_INET, argv[1], &server.sin_addr) <= 0) 
    {
        perror("Invalid address or address not supported");
        exit(1);
    }
    // set up the server address
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(atoi(argv[2]));

    // binds the socket to address and port.
    if (bind(sock, (struct sockaddr *)&server, sizeof server) == -1)
    {
        perror("Error binding socket");
        exit(1);
    }

    length = sizeof(server);

    if (getsockname(sock,(struct sockaddr *) &server,&length) == -1) {
        perror("Error getting socket name");
        exit(2);
    }

    // start listening for client connections
    if (listen(sock, BACKLOG) == -1) 
    {
        perror("Error listening on socket");
        close(sock);
        exit(3);
    }
    printf("Server started and listening on port #%d\n", ntohs(server.sin_port));

    // loop to handle incoming client connections
    do {
        // accept an incoming connection from a client
        client_sock = accept(sock,(struct sockaddr *)&client_addr,(int *) &client_len);
        if (client_sock == -1 ) 
        {
            perror("Error accepting connection");
            exit(4); 
        }


        printf("Connected to client %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // fork a new process to handle the client
        if (fork() == 0) 
        {   
            close(sock);
            handle_client(client_sock);
            exit(0);
        } 
        else 
        {
            close(client_sock);
            wait(NULL); 
        }
    } while(1); // keep looping to accept new connections
    close(sock);
    exit(0);
}