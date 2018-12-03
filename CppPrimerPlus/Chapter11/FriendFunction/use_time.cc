#include<iostream>
#include "my_time.h"

int main() {
  Time t1;
  Time t2(10, 32);
  std::cout << t1 << t2;
  std::cout << t2 * 10 << 10 * t2;
  return 0;
}