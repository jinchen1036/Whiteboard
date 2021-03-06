from collections import defaultdict
import datetime
from DB_Post import update_finalgrade

def login_check(cursor, username, password):

    qry = "SELECT ID, userType, firstName, lastName FROM Users WHERE userName = %s AND password= %s ;"
    cursor.execute(qry, (username, password))

    for (ID, userType, firstName, lastName) in cursor:
        # print("ID = {:d}, userType={:d}".format(ID, userType))
        return {"ID": ID, "userType": userType, "firstName": firstName, "lastName": lastName}

    return -1

def get_Courses(cursor, userID):
    cursor.execute("SELECT userType FROM Users WHERE ID = %s;" % userID)
    for (userType) in cursor:
        uType = userType[0]

    if uType == 1:  # Professor
        cursor.execute("SELECT courseID, courseName,semester,year "
                            "FROM Courses WHERE professorID = %s "
                            "ORDER BY year ASC,semester DESC;" % userID)
    else:  # student
        cursor.execute("SELECT courseID, courseName,semester,year "
                            "FROM Courses NATURAL JOIN TakenClasses "
                            "WHERE studentID = %s "
                            "ORDER BY year ASC,semester DESC;" % userID)
    coursesInfo = []
    for (courseID, courseName, semester, year) in cursor:
        coursesInfo.append({'courseID': courseID, 'courseName': courseName,
                            'semester': semester, 'year': year})

    if not coursesInfo:
        return -1
    return coursesInfo

def get_courseInfo(cursor, courseID):
    qry = "SELECT professorID,courseName, semester,year, firstName,lastName,email " \
          "FROM Users JOIN Courses ON Users.ID = Courses.professorID " \
          "WHERE courseID = %s ORDER BY year ASC,semester DESC;" %courseID
    cursor.execute(qry)

    courseInfo = {}
    for (professorID, courseName, semester, year, firstName, lastName, email) in cursor:
        courseInfo['courseID'] = courseID
        courseInfo['courseName'] = courseName
        courseInfo['semester'] = semester
        courseInfo['year'] = year
        courseInfo['professorID'] = professorID
        courseInfo['professorName'] = firstName + " " + lastName
        courseInfo['professorEmail'] = email

    if not courseInfo:
        return -1
    return courseInfo

def get_Materials(cursor, courseID):
    qry = "SELECT materialID, material,postTime " \
          "FROM ClassMaterial WHERE courseID = %(courseID)s ORDER BY materialID DESC;"
    cursor.execute(qry, {"courseID": courseID})

    materialInfo = []
    for (materialID, content, postTime) in cursor:
        materialInfo.append({'materialID': materialID, 'material': content,
                             'postTime': postTime.strftime("%m/%d/%Y, %H:%M:%S")})

    if not materialInfo:
        return -1
    return materialInfo

def get_Announcement(cursor, courseID):
    qry = "SELECT announcementID, announcement,postTime " \
          "FROM ClassAnnouncement WHERE courseID = %(courseID)s ORDER BY announcementID DESC;"
    cursor.execute(qry, {"courseID": courseID})

    announcementInfo = []
    for (announcementID, content, postTime) in cursor:
        announcementInfo.append({'announcementID': announcementID, 'announcement': content,
                                 'postTime': postTime.strftime("%m/%d/%Y, %H:%M:%S")})
    if not announcementInfo:
        return -1
    return announcementInfo

def get_Assignments(cursor, courseID, ID):
    cursor.execute("SELECT userType FROM Users WHERE ID = %s;" % ID)
    for (userType) in cursor:
        uType = userType[0]


    qry = "SELECT assignmentID, deadline,title, task,gradeTotal,postTime " \
          "FROM Assignment WHERE courseID = %(courseID)s ORDER BY assignmentID DESC;"
    cursor.execute(qry, {"courseID": courseID})

    assignmentInfo = []
    for (assignmentID, deadline, title, task, gradeTotal, postTime) in cursor:
        if deadline < datetime.datetime.now():
            pastDue = True
        else:
            pastDue = False
        assignmentInfo.append({'assignmentID': assignmentID, 'task': task,
                               'gradeTotal': gradeTotal, 'title':title,
                               'deadline': deadline.strftime("%m/%d/%Y, %H:%M:%S"),
                               'postTime': postTime.strftime("%m/%d/%Y, %H:%M:%S"),
                               'pastDue': pastDue
                               })
    if uType == 0:
        for dict in assignmentInfo:
            assignmentID = dict['assignmentID']
            cursor.execute("SELECT submissionID, uploadTime FROM AssignmentSubmission "
                           "WHERE studentID = %s AND assignmentID = %s;" % (ID,assignmentID))
            dict['isSubmitted'] = False
            dict['isLate'] = False
            for (submissionID, uploadTime) in cursor:
                dict['isSubmitted'] = True
                if dict['deadline'] < uploadTime.strftime("%m/%d/%Y, %H:%M:%S"):
                    dict['isLate'] = True

    if not assignmentInfo:
        return -1
    return assignmentInfo


# add isGrade(boolean) and grade (number of none)
def get_submission(cursor, assignmentID):
    cursor.execute("SELECT AssignmentSubmission.submissionID, AssignmentGrade.studentID, "
                   "file, gradeTotal, uploadTime, firstName,lastName,assignmentGrade,deadline "
                   "FROM AssignmentGrade LEFT JOIN AssignmentSubmission "
                   "ON AssignmentGrade.assignmentID = AssignmentSubmission.assignmentID "
                   "AND AssignmentGrade.studentID = AssignmentSubmission.studentID "
                   "LEFT JOIN Assignment ON AssignmentGrade.assignmentID = Assignment.assignmentID "
                   "LEFT JOIN Users ON AssignmentGrade.studentID = Users.ID "
                   "WHERE AssignmentGrade.assignmentID = %s ORDER BY Users.lastName ASC;" % assignmentID)

    submissionInfo = []
    for (submissionID, studentID, file, gradeTotal, uploadTime, firstName, lastName, assignmentGrade,deadline) in cursor:
        pastDue = False
        if deadline < datetime.datetime.now():
            pastDue = True

        isSubmitted,isGrade,isLate = False,False,False
        upTime = None
        if submissionID is not None:
            isSubmitted = True
            upTime = uploadTime.strftime("%m/%d/%Y, %H:%M:%S")
            if deadline < uploadTime:
                isLate = True
            if assignmentGrade is not None:
                isGrade = True
        else:
            isLate = pastDue


        dict = {'submissionID': submissionID, 'studentID': studentID,
                'content': file, 'gradeTotal': gradeTotal,
                'submitTime': upTime, 'assignmentGrade':assignmentGrade,
                'studentName': firstName + ' ' + lastName,
                'isSubmitted': isSubmitted, 'isGraded': isGrade,
                'pastDue': pastDue,'isLate' : isLate
                }
        submissionInfo.append(dict)

    if not submissionInfo:
        return -1
    return submissionInfo



# ################################

# # get_grades
def get_grades(cursor, cnx, courseID,userID):
    cursor.execute("SELECT userType FROM Users WHERE ID = %s;" % userID)
    for (userType) in cursor:
        uType = userType[0]

    sIDs = []
    if uType == 0:  # Student

        cursor.execute("SELECT assignmentPercentage FROM Courses WHERE courseID = %s;" % courseID)
        for (assignmentPercentage) in cursor:
            assignmentPercentage = assignmentPercentage[0]

        cursor.execute("SELECT AssignmentGrade.assignmentID, assignmentGrade,gradeTotal,"
                       "deadline,title, firstName,lastName "
                       "FROM AssignmentGrade LEFT JOIN Assignment "
                       "ON AssignmentGrade.assignmentID = Assignment.assignmentID "
                       "LEFT JOIN Users ON AssignmentGrade.studentID = Users.ID "
                       "WHERE courseID = %s AND studentID = %s "
                       "ORDER BY AssignmentGrade.assignmentID DESC;" % (courseID, userID))
        gradeDict = {"studentID": userID, "name": "",
                        "assignment": [], "assignmentPercentage": assignmentPercentage,
                        "exam": [], "finalGrade": 0}
        for (assignmentID, assignmentGrade, gradeTotal, deadline, title, firstName, lastName) in cursor:
            gradeDict["name"] = firstName + " " + lastName
            gradeDict["assignment"].append({"assignmentID": assignmentID, "assignmentTitle": title,
                                               "assignmentGrade": assignmentGrade, "gradeTotal": gradeTotal})

        cursor.execute("SELECT Exam.examID, examGrade,gradeTotal,examPercentage,description "
                       "FROM  TakenClasses LEFT JOIN Exam "
                       "ON TakenClasses.courseID = Exam.courseID "
                       "LEFT JOIN ExamGrade ON Exam.examID = ExamGrade.examID "
                       "AND ExamGrade.studentID = TakenClasses.studentID "
                       "WHERE TakenClasses.courseID = %s "
                       "AND TakenClasses.studentID = %s "
                       "ORDER BY Exam.examID DESC;" % (courseID, userID))
        for (examID, examGrade, gradeTotal, examPercentage, description) in cursor:
            gradeDict["exam"].append({"examID": examID, "examTitle": description,
                                         "examGrade": examGrade, "examPercentage": examPercentage,
                                         "gradeTotal": gradeTotal
                                         })
        finalGrade = update_finalgrade(cursor, cnx, courseID, userID)
        if finalGrade == False:
            return -1
        else:
            if finalGrade is not None:
                gradeDict["finalGrade"] = round(finalGrade, 2)
            else:
                gradeDict["finalGrade"] = finalGrade





    else:           # Professor
        cursor.execute("SELECT studentID From TakenClasses WHERE courseID = %s;" %courseID)
        for (studentID) in cursor:
            sIDs.append(studentID[0])

        cursor.execute("SELECT assignmentPercentage FROM Courses WHERE courseID = %s;" % courseID)
        for (assignmentPercentage) in cursor:
            assignmentPercentage = assignmentPercentage[0]
        gradeDict ={"percentage":{},"gradeTotal":{}, "title":{},"data":[]}
        gradeDict["percentage"]["assignmentPercentage"] = assignmentPercentage

        get = True
        for studentID in sIDs:
            # get assignment grade

            cursor.execute("SELECT AssignmentGrade.assignmentID, assignmentGrade,gradeTotal,"
                           "deadline,title, firstName,lastName "
                           "FROM AssignmentGrade LEFT JOIN Assignment "
                           "ON AssignmentGrade.assignmentID = Assignment.assignmentID "
                           "LEFT JOIN Users ON AssignmentGrade.studentID = Users.ID "
                           "WHERE courseID = %s AND studentID = %s "
                           "ORDER BY AssignmentGrade.assignmentID ASC;"%(courseID,studentID))

            studentGrade = {"ID": studentID, "name":"", "final":0.0}

            for (assignmentID, assignmentGrade, gradeTotal, deadline,title, firstName, lastName) in cursor:
                studentGrade["name"] = firstName + " " + lastName
                if assignmentID < 10:
                    assignmentName = "as0"+str(assignmentID)
                else: 
                    assignmentName = "as"+str(assignmentID)

                studentGrade[assignmentName]= assignmentGrade

                if get:
                    gradeDict["gradeTotal"][assignmentName] = gradeTotal
                    gradeDict["title"][assignmentName] = title

            #  Get exam grade
            cursor.execute("SELECT Exam.examID, examGrade,gradeTotal,examPercentage,description "
                           "FROM  TakenClasses LEFT JOIN Exam "
                           "ON TakenClasses.courseID = Exam.courseID "
                           "LEFT JOIN ExamGrade ON Exam.examID = ExamGrade.examID "
                           "AND ExamGrade.studentID = TakenClasses.studentID "
                           "WHERE TakenClasses.courseID = %s "
                           "AND TakenClasses.studentID = %s "
                           "ORDER BY Exam.examID ASC;" % (courseID, studentID))
            for(examID,examGrade,gradeTotal,examPercentage,description) in cursor:
                if examID < 10:
                    examName = "ex0"+str(examID)
                else:
                    examName = "ex"+str(examID)

                studentGrade[examName] = examGrade
                if get:
                    gradeDict["gradeTotal"][examName] = gradeTotal
                    gradeDict["title"][examName] = description
                    gradeDict["percentage"][examName] = examPercentage

            finalGrade = update_finalgrade(cursor,cnx, courseID,studentID)
            if finalGrade == False:
                return -1
            else:
                if finalGrade is not None:
                    studentGrade["final"] = round(finalGrade,2)
                else:
                    studentGrade["final"] = finalGrade
            gradeDict['data'].append(studentGrade)

    if not gradeDict:
        return -1
    return gradeDict

