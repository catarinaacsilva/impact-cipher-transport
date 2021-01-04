#include "utils.h"

// Prints data in HEX format on the serial port
void printHex(const char *label, uint8_t *bytes, int len) {
  Serial.printf("%s:\n", label );
  for ( int i = 0; i < len; i++ ) {
    Serial.printf("%02x" , bytes[i] );
  }
  Serial.printf("\n\n");
}

void printBytes(const char *label, uint8_t *bytes, int len) {
  Serial.printf("%s:\n", label );
  for ( int i = 0; i < len; i++) {
    Serial.printf("%02u" , bytes[i] );
  }
  Serial.printf("\n\n");
}

char highHex(uint8_t v) {
  char    c;
  v = ( v >> 4 ) & 0x0F;
  v < 10 ? ( c = '0' + v ) : ( c = 'A' + v - 10 );
  return c;
}

char lowHex(uint8_t v) {
  char    c;
  v = v & 0x0F;
  v < 10 ?  (c = '0' + v) : (c = 'A' + v - 10);
  return c;
}

// Converts a byte array to an HEX string representing the byte array.
void Bytes2Hex(char *out, uint8_t *key, int len) {
  int p = 0;
  for (int i = 0;  i < len ; i++) {
    out[p++] = highHex( key[i] );
    out[p++] = lowHex( key[i] );
  }
  out[p] = '\0';
}

uint8_t nibble( char c )
{
  if ('0' <= c && c <= '9') return (uint8_t)(c - '0');
  if ('A' <= c && c <= 'F') return (uint8_t)(c - 'A' + 10);
  if ('a' <= c && c <= 'f') return (uint8_t)(c - 'a' + 10);
  return 0;
}

uint8_t getByte( char c1 , char c2 ) {
  return ( nibble(c1) << 4 ) | nibble(c2);
}

// Converts a String with an HEX representation into a byte array
void Hex2Bytes( uint8_t *out, const char *in , int len) {
  int p = 0;
  for ( int i = 0 ; i < len ; i = i + 2 ) {
    out[p++] = getByte(in[i] , in[i + 1]);
  }
}

void Char2Bytes(uint8_t *out, const char *in , int len) {
  for (int i = 0 ; i < len ; ++i) {
    out[i] = uint8_t(in[i]);
  }
}

// ESP8266 generate hardware random based numbers.
uint8_t getrnd() {
  //uint8_t really_random = *(volatile uint8_t *)0x3FF20E44;
  uint8_t really_random = esp_random();
  return really_random;
}
