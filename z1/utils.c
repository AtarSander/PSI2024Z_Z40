#include <stdint.h>
#include <stdio.h>

void uint16_to_char(unsigned char *data, uint16_t value, int pos1, int pos2)
{
   data[pos1] = (value >> 8) & 0xFF;
   printf("Data[pos1]= %#x\n", data[pos1]);
   data[pos2] = value & 0xFF;
   printf("Data[pos2]= %#x\n", data[pos2]);
}

uint16_t Fletcher16(unsigned char *data, int length)
{
   uint16_t sum1 = 0;
   uint16_t sum2 = 0;

   for (int index = 0; index < length; ++index)
   {
      sum1 = (sum1 + (int)data[index]) % 255;
      sum2 = (sum2 + sum1) % 255;
   }

   return (sum2 << 8) | sum1;
}

void generate_msg(unsigned char *msg, int length)
{
   if (length == 0)
      msg[0] = 'A';
   else
   {
      char letter = msg[length - 1] + 1;
      if (letter > 'Z')
         letter = 'A';
      msg[length] = letter;
   }
}

uint16_t char_to_uint16(unsigned char byte1, unsigned char byte2)
{
   return (byte1 << 8) | byte2;
}