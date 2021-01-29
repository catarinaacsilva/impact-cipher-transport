#ifndef utils_h
#define utils_h

#include <Arduino.h>

void printHex(const char *label, uint8_t *bytes, int len);
void printBytes(const char *label, uint8_t *bytes, int len);
void Bytes2Hex(char *out, uint8_t *key, int len, int lag);
void Hex2Bytes(uint8_t *out, const char *in , int len, int lag);
void Char2Bytes(uint8_t *out, const char *in , int len);
uint8_t getrnd();

#endif
