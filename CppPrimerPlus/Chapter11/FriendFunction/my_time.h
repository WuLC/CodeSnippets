#ifndef MY_TIME_H
#define MY_TIME_H

#include <iostream>

class Time {
 public:
  Time(int hour = 0, int miniute = 0);
  Time operator*(double m) const;
  // inline function
  friend Time operator*(double m, Time t) {
    return t * m;
  }
  friend std::ostream& operator<<(std::ostream& os, Time t);

 private:
  int hour_;
  int miniute_;
};
#endif