#include <stdint.h>
#include <stdio.h>


// load repeating alphabet characters into data
void generate_msg(unsigned char *msg, int size)
{
   for (int i = 0; i < size; i++)
   {
      if (i == 0)
         msg[0] = 'A';
      else
      {
         char letter = msg[i - 1] + 1;
         if (letter > 'Z')
            letter = 'A';
         msg[i] = letter;
      }
   }
}