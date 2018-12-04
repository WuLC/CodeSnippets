#include "name_space.h"

using per::Person;
using deb::Debt;

int main() {
  Person p = {"lc", "wu"};
  per::Show(p);
  Debt d = {p, 0};
  deb::Show(d);
}