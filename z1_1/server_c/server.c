#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "utils.h"

void main(int argc, char *argv[])
{
    int sock, length;
    uint16_t checksum, calculated_checksum, datagram_length, data_length;
    struct sockaddr_in name, client_addr;
    int client_len = sizeof client_addr;
    char buf[100000] = {0};

    if (argc < 3)
    {
        perror("incorrect arguments");
        exit(4);
    }

    // create a UDP socket
    sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock == -1)
    {
        perror("opening datagram socket");
        exit(1);
    }

    // configure the server address
    name.sin_family = AF_INET;
    inet_pton(AF_INET, argv[1], &name.sin_addr);
    name.sin_port = htons(atoi(argv[2])); // convert port number to network byte order

    // binds the socket to address and port.
    if (bind(sock, (struct sockaddr *)&name, sizeof name) == -1)
    {
        perror("binding datagram socket");
        exit(1);
    }
    length = sizeof(name);

    printf("Server started with port #%d\n", htons(name.sin_port));
    while (1)
    {
        // receive datagram from UDP socket.
        if (recvfrom(sock, buf, 100000, 0, (struct sockaddr *)&client_addr, &client_len) == -1)
        {
            perror("Error receiving datagram packet");
        }

        // reading header data
        datagram_length = char_to_uint16(buf[0], buf[1]);
        data_length = datagram_length - 4;
        checksum = char_to_uint16(buf[2], buf[3]);
        char *data = buf + 4;

        // validate the received data
        calculated_checksum = Fletcher16(data, data_length);
        if (checksum != calculated_checksum)
        {
            perror("Checksum incorrect!");
            exit(3);
        }

        // printing received data
        // data[data_length] = '\0';
        // printf("Received data: %s", data);

        // prepare the response datagram header
        uint16_to_char(buf, calculated_checksum, 2, 3);

        // sending response back to the client
        if (sendto(sock, buf, 4, 0,
                   (struct sockaddr *)&client_addr, client_len) == -1)
            perror("Error sending datagram response");
    }
    close(sock);
    exit(0);
}