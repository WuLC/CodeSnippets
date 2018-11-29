#ifndef MY_TIME_H_
#define MY_TIME_H_

class Time {
 public:
   Time(int hour = 0, int minute = 0);
   void Reset(int hour = 0, int minute = 0);
   void Show() const;
   Time operator+(const Time& t) const;

 private:
   int minute_;
   int hour_;
};

#endif // !MY_TIME_H_
