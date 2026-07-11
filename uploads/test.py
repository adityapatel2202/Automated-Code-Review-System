# name = input("Enter your name: ")
# age = int(input("Enter your age: "))    

# class Student:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age

# student1 = Student(name, age)
# # print(student1.name)  # Output: Alice
# # print(student1.age)   # Output: 20

# # print(f"Student Name: {student1.name}, Student Age: {student1.age}")
# # or
# def display_info(self):
#         print(f"Student Name: {self.name}, Student Age: {self.age}")

# Student.display_info = display_info
# student1.display_info() 


# or

# name = input("Enter your name: ")
# age = int(input("Enter your age: "))    

# class Student:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#     def display_info(self):
#         print(f"Student Name: {self.name}, Student Age: {self.age}")  

# student1 = Student(name, age)
# student1.display_info()

# REPITITION FOR STUDENT NAME AND ID AND AGE
name = input("Enter your name: ")
age = int(input("Enter your age: "))  


student_id = 0;
class Student:
    def __init__(self, name, age, student_id):
        self.name = name
        self.age = age

    def get_id(self):
        global student_id
        student_id += 1
        return student_id


    def display_info(self):
        print(f"............\nStudent ID: {self.get_id()}\nStudent Name: {self.name}\nStudent Age: {self.age}\n............")

student1 = Student(name, age, student_id)
student1.display_info()