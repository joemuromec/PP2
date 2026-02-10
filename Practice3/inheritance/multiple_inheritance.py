class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)
    
class Rocker:
    def play_guitar(self):
        print("Turururutuiiii!!!")
        
# Add a method called welcome to the Student class:
class Student(Person, Rocker):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear)
    
x = Student("Mike", "Olsen", 2024)
x.play_guitar()

