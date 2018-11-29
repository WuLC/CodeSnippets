#include<iostream>
#include "my_time.h"

int main() {
  Time t1;
  Time t2(10, 5);
  Time t3(20, 3);
  t1.Show();
  t2.Show();
  t3.Show();

  Time t4 = t2 + t3;
  t4.Show();

  Time t5 = t1.operator+(t3);
  t5.Show();
  t5.Reset();
  t5.Show();
  std::cin.get();
  return 0;
}