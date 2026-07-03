class Student:
    
    # Constructor
    def __init__(self):
        self.__student_id = None
        self.__student_name =None

    #setter methods
    def set_student_id(self, student_id):
        self.__student_id = student_id

    def set_student_name(self, student_name):
        self.__student_name = student_name

    # Getter methods
    def get_student_id(self):
        return self.__student_id
    def get_student_name(self):
        return self.__student_name
    
student1 = Student()
print("Enter student id: ")
student_id = int(input())
print("Enter student name: ")
student_name = input()
student1.set_student_id(student_id)
student1.set_student_name(student_name)
print("\n'''''''''''''''")
print(f"Student ID: {student1.get_student_id()}")
print(f"Student Name: {student1.get_student_name()}")
print("'''''''''''''''\n")
