#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "utils.h"

#define BUF_SIZE (100 * 1024) // set buffer size to 100 KB


int main(int argc, char *argv[])
{
    int sock;                       // socket file descriptor
    struct sockaddr_in server;      // struct to define server address
    struct hostent *hp;             // host information struct for resolving the hostname
    char *data = malloc(BUF_SIZE);  // allocate buffer for data to be sent
    char buffer[BUF_SIZE];          // buffer for reading responses from the server
    int bytes_read = 0;
    int total_bytes_read = 0;

    // check if data allocation was successful
    if (data == NULL) 
    {
        perror("Error allocating memory for data buffer");
        exit(1);
    }

    if (argc < 3)
    {
        fprintf(stderr, "Usage: %s <host> <port>\n", argv[0]);
        exit(1);
    }
    char *HOST = argv[1]; // host read from input arguments

    // create a TCP socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        perror("Error opening stream socket");
        free(data);
        exit(2);
    }

    // resolve the hostname to an IP address
    hp = gethostbyname(HOST);
    if (hp == (struct hostent *)0)
    {
        fprintf(stderr, "%s: unknown host\n", HOST);
        free(data);
        close(sock);
        exit(3);
    }

    // set up the server address
    server.sin_family = AF_INET;                                        // use IPv4
    server.sin_port = htons(atoi(argv[2]));                             // convert port number to network byte order
    memcpy((char *)&server.sin_addr, (char *)hp->h_addr, hp->h_length); // copy the resolved IP address

    // connect to the server
    if (connect(sock, (struct sockaddr *) &server, sizeof server) == -1) 
    {
        perror("Error connecting to stream socket");
        free(data);
        close(sock);
        exit(4);
    }

    // generate the message to send
    generate_msg(data, BUF_SIZE);
    sleep(5); 
    // send the data to the server
    if (write(sock, data, sizeof data) == -1)
    {
        perror("Error writing to stream socket");
        free(data);  
        close(sock); 
        exit(5);
    }
        
    // receive response from the server   
    while ((bytes_read = read(sock, buffer, BUF_SIZE)) > 0) 
    {
        total_bytes_read += bytes_read;
    }
    printf("Received %d bytes from server\n", total_bytes_read);

    if (bytes_read == -1) 
    {
        perror("Error reading from stream socket");
    }

    // clean up and close the connection
    free(data);
    close(sock);
    exit(0);
}