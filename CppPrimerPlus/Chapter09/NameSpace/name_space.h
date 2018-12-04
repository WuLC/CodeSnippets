#include <string>

namespace per {
  struct Person {
    std::string first_name;
    std::string last_name;
  };

  void Show(Person& p);
}

namespace deb {

  using per::Person;
  struct Debt {
    Person p;
    double debt;
  };

  void Show(Debt& d);
}