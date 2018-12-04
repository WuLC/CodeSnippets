#include "name_space.h"

#include <iostream>

namespace per{
  void Show(Person& p) {
    std::cout << "first name:" << p.first_name << ", last name:" << p.last_name << std::endl;
  }
}

namespace deb {
  void Show(Debt& d) {
    std::cout << "first name:" << d.p.first_name << ", last name:" << d.p.last_name << ", debt:" << d.debt << std::endl;
  }
}