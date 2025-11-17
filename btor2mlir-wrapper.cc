#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>

extern "C" int _main();
extern "C" long long sim_counter = 0;

void summary() {
  printf("simulation cycle: %lld\n", sim_counter);  
}

void term_handler(int sig) {
  summary();
  exit(0);
}

int main(int argc, char** argv) {
  struct sigaction sa = {0};
  sa.sa_handler = term_handler;
  if(sigaction(SIGINT, &sa, NULL)) {
    perror("fail to set sigint");
    return 1;
  }
  if(sigaction(SIGTERM, &sa, NULL)) {
    perror("fail to set sigterm");
    return 1;
  }
  _main();
  summary();
}
