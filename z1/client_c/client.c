#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "../utils.h"

int MAX_LENGTH = 100000;

int main(int argc, char *argv[])
{
    int sock;
    struct sockaddr_in name;
    struct hostent *hp;
    char buf[5] = {0};

    sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock == -1)
    {
        perror("opening datagram socket");
        exit(1);
    }
    // hp = gethostbyname(argv[1]);
    hp = gethostbyname("0.0.0.0");

    if (hp == (struct hostent *)0)
    {
        // fprintf(stderr, "%s: unknown host\n", argv[1]);
        fprintf(stderr, "%s: unknown host\n", "0.0.0.0");
        exit(2);
    }

    // Ustawienie adresu hosta
    memcpy((char *)&name.sin_addr, (char *)hp->h_addr,
           hp->h_length);
    name.sin_family = AF_INET;
    // name.sin_port = htons(atoi(argv[2]));
    name.sin_port = htons(8000);
    unsigned char *datagram = malloc(MAX_LENGTH + 5);
    unsigned char *msg = malloc(MAX_LENGTH + 1);
    uint16_t response_checksum;
    uint16_t response_length;
    for (uint16_t length = 0; length < MAX_LENGTH; ++length)
    {
        generate_msg(msg, length);
        uint16_t checksum = Fletcher16(msg, length + 1);
        printf("Checksum %#x\n", checksum);
        uint16_to_char(datagram, length + 1, 0, 1);
        uint16_to_char(datagram, checksum, 2, 3);
        memcpy(datagram + 4, msg, length + 2);

        printf("Datagram: %u\n", datagram);
        if (sendto(sock, datagram, length + 5, 0,
                   (struct sockaddr *)&name, sizeof name) == -1)
            perror("sending datagram message");

        if (read(sock, buf, 5) == -1)
        {
            perror("receiving datagram packet");
            exit(2);
        }
        response_length = char_to_uint16(buf[0], buf[1]);
        response_checksum = char_to_uint16(buf[2], buf[3]);
        if (response_length == length + 1 && response_checksum == checksum)
            printf("Communication successful\n");
        else
        {
            perror("Communication failed!");
            exit(3);
        }
    }

    close(sock);
    exit(0);
}