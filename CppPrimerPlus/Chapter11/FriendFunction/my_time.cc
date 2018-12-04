#include "my_time.h"

#include <iostream>

Time::Time(int hour, int miniute) {
  hour_ = hour;
  miniute_ = miniute;
}

Time Time::operator*(double m) const{
  Time t;
  t.hour_ = this->hour_ * m;
  t.miniute_ = this->miniute_ * m;
  return t; 
}

std::ostream& operator<<(std::ostream& os, Time t) {
  os << "hour:" << t.hour_ << ", miniute:" << t.miniute_ << std::endl;
  return os;
}