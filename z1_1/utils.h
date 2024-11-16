#ifndef UTILS_H
#define UTILS_H
void uint16_to_char(unsigned char *data, uint16_t value, int pos1, int pos2);
uint16_t char_to_uint16(unsigned char byte1, unsigned char byte2);
uint16_t Fletcher16(uint8_t *data, int count);
void generate_msg(unsigned char *msg, int index);
#endif