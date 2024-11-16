#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "utils.h"

int MAX_LENGTH = 100000;

int main(int argc, char *argv[])
{
    int sock;                // socket file descriptor
    struct sockaddr_in name; // struct to define server address
    struct hostent *hp;      // host information struct for resolving the hostname
    char buf[5] = {0};       // buffer for reading responses from the server
    if (argc < 3)
    {
        perror("incorrect arguments");
        exit(1);
    }
    char *HOST = argv[1]; // host read from input arguments

    // create a UDP socket
    sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock == -1)
    {
        perror("Error opening datagram socket");
        exit(2);
    }
    // resolve the hostname to an IP address
    hp = gethostbyname(HOST);

    if (hp == (struct hostent *)0)
    {
        fprintf(stderr, "%s: unknown host\n", HOST);
        exit(3);
    }

    // copy the resolved IP address to the name struct
    memcpy((char *)&name.sin_addr, (char *)hp->h_addr,
           hp->h_length);
    name.sin_family = AF_INET;
    name.sin_port = htons(atoi(argv[2])); // convert port number to network byte order

    unsigned char *datagram = malloc(MAX_LENGTH + 5); // datagram includes 4 bytes for metadata + message
    unsigned char *msg = malloc(MAX_LENGTH + 1);      // message buffer
    uint16_t response_checksum;
    uint16_t response_length;

    for (uint16_t length = 0; length < MAX_LENGTH; ++length)
    {
        generate_msg(msg, length);
        uint16_t checksum = Fletcher16(msg, length + 1);
        // add metadata (length and checksum) to the datagram
        uint16_to_char(datagram, length + 5, 0, 1);
        uint16_to_char(datagram, checksum, 2, 3);
        memcpy(datagram + 4, msg, length + 2);

        // log created data headers
        printf("Datagram length: %u\n", length + 5);
        printf("Checksum: %u\n", checksum);

        // send the datagram to the server
        if (sendto(sock, datagram, length + 5, 0,
                   (struct sockaddr *)&name, sizeof name) == -1)
            perror("Error sending datagram message");

        // read the server's response into the buffer
        if (read(sock, buf, 5) == -1)
        {
            perror("Error receiving datagram packet");
            exit(4);
        }
        // extract response length and checksum
        response_length = char_to_uint16(buf[0], buf[1]);
        response_checksum = char_to_uint16(buf[2], buf[3]);
        // validate the response
        if (response_checksum == checksum)
            printf("Response#%u correct\n", length + 1);
        else
        {
            printf("Response#%u incorrect\n", length + 1);
            exit(5);
        }
    }

    close(sock);
    exit(0);
}