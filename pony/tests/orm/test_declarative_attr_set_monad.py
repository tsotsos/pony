import unittest
from pony.orm import *
from testutils import *

db = Database('sqlite', ':memory:')

class Student(db.Entity):
    name = Required(unicode)
    scholarship = Optional(int)
    group = Required("Group")
    marks = Set("Mark")

class Group(db.Entity):
    number = PrimaryKey(int)
    department = Required(int)
    students = Set(Student)
    subjects = Set("Subject")

class Subject(db.Entity):
    name = PrimaryKey(unicode)
    groups = Set(Group)
    marks = Set("Mark")

class Mark(db.Entity):
    value = Required(int)
    student = Required(Student)
    subject = Required(Subject)
    PrimaryKey(student, subject)

db.generate_mapping(create_tables=True)

@with_transaction
def populate_db():
    g41 = Group(number=41, department=101)
    g42 = Group(number=42, department=102)
    g43 = Group(number=43, department=102)

    s1 = Student(id=1, name="Joe", scholarship=None, group=g41)
    s2 = Student(id=2, name="Bob", scholarship=100, group=g41)
    s3 = Student(id=3, name="Beth", scholarship=500, group=g41)
    s4 = Student(id=4, name="Jon", scholarship=500, group=g42)
    s5 = Student(id=5, name="Pete", scholarship=700, group=g42)

    Math = Subject(name="Math")
    Physics = Subject(name="Physics")
    History = Subject(name="History")

    g41.subjects = [ Math, Physics, History ]
    g42.subjects = [ Math, Physics ]
    g43.subjects = [ Physics ]

    Mark(value=5, student=s1, subject=Math)
    Mark(value=4, student=s2, subject=Physics)
    Mark(value=3, student=s2, subject=Math)
    Mark(value=2, student=s2, subject=History)
    Mark(value=1, student=s3, subject=History)
    Mark(value=2, student=s3, subject=Math)
    Mark(value=2, student=s4, subject=Math)
populate_db()

class TestAttrSetMonad(unittest.TestCase):
    def setUp(self):
        rollback()
    def tearDown(self):
        rollback()

    def test1(self):
        groups = fetch_all(g for g in Group if len(g.students) > 2)
        self.assertEqual(groups, [Group[41]])
    def test2(self):
        groups = set(fetch_all(g for g in Group if len(g.students.name) >= 2))
        self.assertEqual(groups, set([Group[41], Group[42]]))
    def test3(self):
        groups = fetch_all(g for g in Group if len(g.students.marks) > 2)
        self.assertEqual(groups, [Group[41]])
    def test4(self):
        groups = fetch_all(g for g in Group if max(g.students.marks.value) <= 2)
        self.assertEqual(groups, [Group[42]])
    def test5(self):
        students = fetch_all(s for s in Student if len(s.marks.subject.name) > 5)
        self.assertEqual(students, [])
    def test6(self):
        students = set(fetch_all(s for s in Student if len(s.marks.subject) >= 2))
        self.assertEqual(students, set([Student[2], Student[3]]))
    def test8(self):
        students = set(fetch_all(s for s in Student if s.group in (g for g in Group if g.department == 101)))
        self.assertEqual(students, set([Student[1], Student[2], Student[3]]))
    def test9(self):
        students = set(fetch_all(s for s in Student if s.group not in (g for g in Group if g.department == 101)))
        self.assertEqual(students, set([Student[4], Student[5]]))
    def test10(self):
        students = set(fetch_all(s for s in Student if s.group in (g for g in Group if g.department == 101)))
        self.assertEqual(students, set([Student[1], Student[2], Student[3]]))
    def test11(self):
        students = set(fetch_all(g for g in Group if len(g.subjects.groups.subjects) > 1))
        self.assertEqual(students, set([Group[41], Group[42], Group[43]]))
    def test12(self):
        groups = set(fetch_all(g for g in Group if len(g.subjects) >= 2))
        self.assertEqual(groups, set([Group[41], Group[42]]))
    def test13(self):
        groups = set(fetch_all(g for g in Group if g.students))
        self.assertEqual(groups, set([Group[41], Group[42]]))
    def test14(self):
        groups = set(fetch_all(g for g in Group if not g.students))
        self.assertEqual(groups, set([Group[43]]))
    def test15(self):
        groups = set(fetch_all(g for g in Group if exists(g.students)))
        self.assertEqual(groups, set([Group[41], Group[42]]))
    def test15a(self):
        groups = set(fetch_all(g for g in Group if not not exists(g.students)))
        self.assertEqual(groups, set([Group[41], Group[42]]))
    def test16(self):
        groups = fetch_all(g for g in Group if not exists(g.students))
        self.assertEqual(groups, [Group[43]])
    def test17(self):
        groups = set(fetch_all(g for g in Group if 100 in g.students.scholarship))
        self.assertEqual(groups, set([Group[41]]))        
    def test18(self):
        groups = set(fetch_all(g for g in Group if 100 not in g.students.scholarship))
        self.assertEqual(groups, set([Group[42], Group[43]]))
    def test19(self):
        groups = set(fetch_all(g for g in Group if not not not 100 not in g.students.scholarship))
        self.assertEqual(groups, set([Group[41]]))
    def test20(self):
        groups = set(fetch_all(g for g in Group if exists(s for s in Student if s.group == g and s.scholarship == 500)))
        self.assertEqual(groups, set([Group[41], Group[42]]))
    def test21(self):
        groups = set(fetch_all(g for g in Group if g.department is not None))
        self.assertEqual(groups, set([Group[41], Group[42], Group[43]]))
    def test21a(self):
        groups = set(fetch_all(g for g in Group if not g.department is not None))
        self.assertEqual(groups, set([]))
    def test21b(self):
        groups = set(fetch_all(g for g in Group if not not not g.department is None))
        self.assertEqual(groups, set([Group[41], Group[42], Group[43]]))   
    def test22(self):
        groups = set(fetch_all(g for g in Group if 700 in (s.scholarship for s in Student if s.group == g)))
        self.assertEqual(groups, set([Group[42]]))
    def test23a(self):
        groups = set(fetch_all(g for g in Group if 700 not in g.students.scholarship))
        self.assertEqual(groups, set([Group[41], Group[43]]))
    def test23b(self):
        groups = set(fetch_all(g for g in Group if 700 not in (s.scholarship for s in Student if s.group == g)))
        self.assertEqual(groups, set([Group[41], Group[43]]))
    @raises_exception(NotImplementedError)
    def test24(self):
        groups = set(fetch_all(g for g in Group for g2 in Group if g.students == g2.students))
    def test25(self):
        m1 = Mark[Student[1], Subject["Math"]]
        students = set(fetch_all(s for s in Student if m1 in s.marks))
        self.assertEqual(students, set([Student[1]]))
    def test26(self):
        s1 = Student[1]
        groups = set(fetch_all(g for g in Group if s1 in g.students))
        self.assertEqual(groups, set([Group[41]]))
    @raises_exception(AttributeError, 'g.students.name.foo')
    def test27(self):
        fetch_all(g for g in Group if g.students.name.foo == 1)        

if __name__ == "__main__":
    unittest.main()
