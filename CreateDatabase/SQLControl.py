#!/usr/bin/env python
# If you don't have mysql.connect library
# Run `pip install mysql-connector` to install

import mysql.connector
from mysql.connector import errorcode
from SQLInit import init
from SQLCreate import *
from SQLQuery import *

config = {
    "user": '',    # your mysql username
    "password": '',  # your mysql password
    "host": '127.0.0.1',
}
# Set your own database name
database = 'Whiteboard'

def create_type(type,cursor,num):
    if type == "Users":
        create_random_users(cursor, num)
    elif type == "Courses":
        create_random_courses(cursor, num)
    elif type =="TakenClasses":
        create_random_takenClasses(cursor,num)
    elif type == "Assignment":
        create_random_assignment(cursor, num,7)
    elif type =="AssignmentSubmission":
        create_random_assignmentSubmission(cursor,num)
    elif type == "Exam":
        create_random_exam(cursor, num)
    elif type == "GradeBook":
        create_random_gradeBook(cursor, num)
    elif type == "ClassAnnouncement":
        create_random_classAnnouncement(cursor, num)
    elif type == "ClassMaterials":
        create_random_classMaterials(cursor,num)

    else:
        print(f"Unknown Typle : {type}")


def query_type(type,cursor):
    if type == "Users":
        query_users(cursor)
    elif type == "Courses":
        query_courses(cursor)
    elif type =="TakenClasses":
        query_takenClasses(cursor)
    elif type == "Assignment":
        query_assignment(cursor)
    elif type =="AssignmentSubmission":
        query_assignmentSubmission(cursor)
    elif type == "Exam":
        query_exam(cursor)
    elif type == "GradeBook":
        query_gradeBook(cursor)
    elif type =="ClassAnnouncement":
        query_classAnnouncement(cursor)
    elif type =="ClassMaterials":
        query_classMaterials(cursor)
    else:
        print(f"Unknown Typle : {type}")



def main(argv,type,num, database):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(buffered=True)
        if argv == "init":
            print("init")
            init(cursor, database)
            cnx.commit()        # Make sure data is committed to the database
        elif argv == "create":
            print("create")
            cursor.execute("USE %s;" % database)
            create_type(type, cursor, num)
            cnx.commit()            # Make sure data is committed to the database
        elif argv == "query":
            print("query")
            cursor.execute("USE %s;" % database)
            query_type(type, cursor)
        else:
            print("Drop Database")
            cursor.execute("DROP DATABASE IF EXISTS %s;" % database)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        raise err
    else:
        cnx.close()




table = ["Users","Courses","TakenClasses","Assignment","AssignmentSubmission","Exam","GradeBook","ClassAnnouncement","ClassMaterials"]
action = ["init", "create","query","deleteDB"]
nums = [50,4,50,10,30,10,30,6,6]
num = 5

main("",type,num,database)

# init database and all table:
main(action[0],type,num,database)


# Create Table
for i in range(9):
    main(action[1], table[i], nums[i],database)
    print(table[i])

# Query from Database
for i in range(9):
    print(table[i])
    main(action[2], table[i], nums[i],database)

