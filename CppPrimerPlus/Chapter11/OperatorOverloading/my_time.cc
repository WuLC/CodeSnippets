#include<iostream>
#include "my_time.h"


Time::Time(int hour, int minute) {
  hour_ = hour;
  minute_ = minute;
}
 
void Time::Reset(int hour, int minute) {
  hour_ = hour;
  minute_ = minute;
}

void Time::Show() const {
  std::cout << "hour:" << hour_ << " ,minute:" << minute_ << std::endl;
}

Time Time::operator+(const Time& t) const {
  Time sum;
  sum.minute_ = this->minute_ + t.minute_;
  sum.hour_ = (this->hour_ + t.hour_ + int(sum.minute_ / 60)) % 24;
  sum.minute_ %= 60;
  return sum;
}