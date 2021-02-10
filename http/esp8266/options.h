#ifndef options_h
#define options_h

// WIFI login
#define SSID "TheOffice"
#define PASSWORD "8006002030"

// Diffie Hellman key exchange (curve25519; p521)
#define DH_25519
//#define DH_521

// Cipher Algorithm (AES; ChaCha)
#define CA_AES
//#define CA_CHACHA

// Cipher algorithm key size (128; 192; 256)
#define KS_128
//#define KS_192
//#define KS_256

#ifdef DH_25519
  #define KEY_SIZE_PUBLIC 32
  #define KEY_SIZE_PRIVAT 32
#else
  #define KEY_SIZE_PUBLIC 132
  #define KEY_SIZE_PRIVAT 66
#endif

#if defined(KS_256) || defined(CA_CHACHA)
  #define SESSION_KEY_SIZE 32
#elif defined(KS_192)
  #define SESSION_KEY_SIZE 24
#else
  #define SESSION_KEY_SIZE 16
#endif

// Links to communicate with the REST server
#define KEY_EXCHANGE_POST "http://192.168.1.128:5000/putkey/sensor"
#define KEY_EXCHANGE_GET "http://192.168.1.128:5000/getkey/client"
#define DATA_POST "http://192.168.1.128:5000/putdata/client"

// NTP Definitions
//#define NTP_SERVER "time.ua.pt"
#define NTP_SERVER "1.pt.pool.ntp.org"
// Update NTP every 10 min (600 seconds)
#define NTP_INTERVAL 600

// JSON Message buffer size
#define LENGTH 128

#endif
