from _json import make_encoder
from aifc import Error
from ctypes import c_ubyte

from app.databaseconn import mydb

def getRole(idroles):
    cursor = mydb.cursor()
    query_string = "SELECT rolename FROM roles WHERE idroles = %s"
    cursor.execute(query_string, (idroles,))
    data = cursor.fetchall()
    return data[0]

def getSalt(emailid):
    cursor = mydb.cursor()
    query_string = "SELECT salt FROM users WHERE emailid = %s"
    cursor.execute(query_string, (emailid,))
    data = cursor.fetchall()
    print(data)
    if len(data) == 0 :
        return 'fake'
    return data[0][0]

def getResourceId(resourcename):
    cursor = mydb.cursor()
    query_string = "SELECT idresources FROM resources WHERE name = %s"
    cursor.execute(query_string, (resourcename,))
    data = cursor.fetchall()
    return str(data[0][0])

def getPermissions(idroles, resourcename):
    idresources = getResourceId(resourcename)
    cursor = mydb.cursor()
    # print('idres ',idresources,' idrole',idroles)
    query_string = "SELECT idroleresource FROM roleresource WHERE idroles = %s AND idresources = %s"
    cursor.execute(query_string, (idroles, idresources,))
    idroleresources = cursor.fetchall()
    if(len(idroleresources)>0):
        print(idroleresources[0][0])
        query_string = "SELECT idoperations, constraints FROM permissions WHERE idroleresource = %s"
        cursor.execute(query_string, (idroleresources[0][0],))
        data = cursor.fetchall()
    else:
        data = []
    operationsconstraints = []
    if len(data) == 0:
        operationsconstraints.append(['none', 'none'])
    for i in data:
        constraints = i[1]
        query_string = "SELECT operationname FROM operations WHERE idoperations = %s"
        cursor.execute(query_string, (i[0],))
        operationname= cursor.fetchall()
        operationsconstraints.append([operationname[0][0], constraints])
    return operationsconstraints

def getUserCourseIDs(idusers):
    cursor = mydb.cursor()
    # print('idres ',idresources,' idrole',idroles)
    query_string = "SELECT idcourses FROM userscourses WHERE idusers = %s"
    cursor.execute(query_string, (idusers,))
    idcourses = cursor.fetchall()
    print('ID coursesss ',idcourses)
    return idcourses

def getUserCoursesIdName(idusers):
    idcourses = getUserCourseIDs(idusers = idusers)
    cursor = mydb.cursor()
    print('ID courses ',idcourses)
    coursesidname = []
    # print('idres ',idresources,' idrole',idroles)
    for i in idcourses:
        query_string = "SELECT coursesname FROM courses WHERE idcourses = %s"
        cursor.execute(query_string, (i[0],))
        data = cursor.fetchall()
        coursesidname.append([i[0], data[0][0]])
    return coursesidname

def getUserCoursesMarks(idusers, idcourses):
    # idcourses = getUserCourseIDs(idusers = idusers)
    cursor = mydb.cursor()

    query_string = "SELECT marks FROM "+'`'+idcourses+'`'+" WHERE idusers = %s"
    cursor.execute(query_string, (idusers,))
    coursemarks = cursor.fetchall()

    # print(float(coursemarks[0][0]))
    return float(coursemarks[0][0])

def getAllMarksOneCourse(idcourses):
    # idcourses = getUserCourseIDs(idusers = idusers)
    cursor = mydb.cursor()
    # coursesmarks = []
    # print('idres ',idresources,' idrole',idroles)
    # print(idcourses)
    # coursetable = str('`'+idcourses+'`')
    # print(coursetable)
    query_string = "SELECT * FROM "+'`'+idcourses+'`'
    cursor.execute(query_string, ())
    coursemarks = cursor.fetchall()

    # print(float(coursemarks[0][0]))
    return coursemarks

def verifyPermissions(permissionon,resourcename,operation):
    boolperm = False
    const = ['none']
    perms = permissionon[resourcename]
    print('permission on ',resourcename,' are ',perms)
    prems = perms['permissions']
    print('prems on ',prems)
    for i in prems:
        if i[0] == operation:
            const = []
            boolperm =True
            j = i[1].split('|')
            for k in j:
                const.append(k)
    return boolperm,const

def getOwnMarks(idusers,idcourses):
    data = [idusers,getUserCoursesMarks(idusers,idcourses)]
    print('all marks: ',[data])
    data = [data]
    return data

def getMarks(idcourses):
    marks = getAllMarksOneCourse(idcourses)
    # data = []
    # for i in marks:
    #     data.append([])
    print('all marks: ',marks)
    return marks

def getAllStudentCourseMarks(idcourses):
    cursor = mydb.cursor()
    # coursesmarks = []
    # print('idres ',idresources,' idrole',idroles)
    # print(idcourses)
    # coursetable = str('`'+idcourses+'`')
    # print(coursetable)
    query_string = "SELECT * FROM " + '`' + idcourses + '`'
    cursor.execute(query_string, ())
    studentmarks = cursor.fetchall()
    return studentmarks

def getStudentInCourse(idcourses):
    cursor = mydb.cursor()
    # coursesmarks = []
    # print('idres ',idresources,' idrole',idroles)
    # print(idcourses)
    # coursetable = str('`'+idcourses+'`')
    # print(coursetable)
    query_string = "SELECT idusers FROM " + '`' + idcourses + '`'
    cursor.execute(query_string, ())
    students = cursor.fetchall()
    return students

def checkUserCourse(idusers, idcourses):
    cursor = mydb.cursor()
    # coursesmarks = []
    # print('idres ',idresources,' idrole',idroles)
    # print(idcourses)
    # coursetable = str('`'+idcourses+'`')
    # print(coursetable)
    query_string = "SELECT * FROM userscourses WHERE idusers = %s and idcourses = %s"
    cursor.execute(query_string, (idusers,idcourses,))
    data = cursor.fetchall()
    print('Check User Course: ',data)
    if(len(data) == 0):
        return False
    return True

def getRoleIdByName(rolename):
    cursor = mydb.cursor()
    query_string = "SELECT idroles FROM roles WHERE rolename = %s"
    cursor.execute(query_string, (rolename,))
    data = cursor.fetchall()
    idroles = data[0]
    return idroles[0]

def getNotAssignedUsers(idcourses,rolename):
    print(idcourses)
    idroles = getRoleIdByName(rolename)
    cursor = mydb.cursor()

    query_string1 = "SELECT a.idusers FROM users as a WHERE idroles = "+str(idroles)
    query_string2 = "SELECT b.idusers FROM userscourses as b WHERE idcourses = '"+str(idcourses)+"'";
    query_string = query_string1+" AND a.idusers NOT IN ("+query_string2+")"
    cursor.execute(query_string)
    data = cursor.fetchall()
    return data

def addStudentInCourse(idcourses,idusers):
    cursor = mydb.cursor()
    for iduser in idusers:
        query_string = "INSERT INTO userscourses(idusers, idcourses) VALUES (%s ,%s)"
        cursor.execute(query_string, (str(iduser),str(idcourses)))
        query_string = "INSERT INTO "+idcourses+"(idusers,marks) VALUES (%s,-1)"
        cursor.execute(query_string, (str(iduser),))
    mydb.commit()
    print('Adding Student Success!')

def getTAInCourse(idcourses,rolename):
    # print(idcourses)
    idroles = getRoleIdByName(rolename)
    cursor = mydb.cursor()
    query_string1 = "SELECT a.idusers FROM users as a WHERE idroles = "+str(idroles)
    query_string2 = "SELECT b.idusers FROM userscourses as b WHERE idcourses = '"+str(idcourses)+"'";
    query_string = query_string1+" AND a.idusers IN ("+query_string2+")"
    cursor.execute(query_string)
    ta = cursor.fetchall()
    print('Ta in ',idcourses,' are ',ta)
    return ta

def addUserInCourse(idcourses,idusers):
    cursor = mydb.cursor()
    for iduser in idusers:
        query_string = "INSERT INTO userscourses(idusers, idcourses) VALUES (%s ,%s)"
        cursor.execute(query_string, (str(iduser),str(idcourses)))
    mydb.commit()
    print('Adding TA Success!')


def removeUserFromCourse(idcourses,idusers):
    cursor = mydb.cursor()
    print(idcourses,' -- ',idusers)
    for iduser in idusers:
        query_string = "DELETE FROM userscourses WHERE idusers = %s AND idcourses = %s"
                       # "INSERT INTO userscourses(idusers, idcourses) VALUES (%s ,%s)"

        # try:
        cursor.execute(query_string, (str(iduser), str(idcourses)))

            # accept the change
            # cursor.commit()
        # except Error as error:
        #     print(error)

        # finally:
            # cursor.close()
            # conn.close()
        # cursor.execute(query_string, (str(iduser),str(idcourses)))
        mydb.commit()
        print('Removed TA Success!')
        # query_string = "INSERT INTO "+idcourses+"(idusers) VALUES (%s)"
        # cursor.execute(query_string, (str(iduser),))

    mydb.commit()
    cursor.execute('SELECT * FROM userscourses')
    records = cursor.fetchall()
    for record in records:
        print(record)

def getAllMarksFromCourse(idcourses):
    cursor = mydb.cursor()
    query_string = "SELECT idusers,marks FROM "+ idcourses;
    cursor.execute(query_string)
    idusersmarks = cursor.fetchall()
    print('All marks for ',idcourses,' are ',idusersmarks)
    return idusersmarks

def insertEditedMarksInCourse(idcourses, idusers, marks):
    cursor = mydb.cursor()
    for i in range(0,len(idusers)):
        try:
            marks[i] = float(marks[i])
            query_string = "UPDATE " + idcourses + ' SET marks = %s WHERE idusers = %s'
            cursor.execute(query_string, (str(marks[i]), str(idusers[i]),))
            mydb.commit()
        except ValueError:
            print('Non Int Input, not updated!')
    print('Marks Successfully Updated!')

def deleteStudentMarks(idcourses, idusers):
    cursor = mydb.cursor()
    for i in range(0, len(idusers)):
        query_string = "UPDATE " + idcourses + ' SET marks = %s WHERE idusers = %s'
        cursor.execute(query_string, ('-1', str(idusers[i]),))

    mydb.commit()
    print('Marks Successfully Updated!')

def getAllExistingCourses():
    # print(idcourses)
    cursor = mydb.cursor()
    query_string = "SELECT * FROM courses";
    cursor.execute(query_string)
    courses = cursor.fetchall()
    print('Courses Existing are ',courses)
    return courses

def addNewCourse(idcourses,coursesname):
    courses = getAllExistingCourses()
    flag = True
    for i in courses:
        if(i[0] == idcourses):
            flag = False
    res = 'Course ID already existing!'
    if(flag):
        cursor = mydb.cursor()
        query_string = "INSERT INTO courses(idcourses,coursesname) VALUES (%s ,%s)"
        try:
            cursor.execute(query_string, (str(idcourses),str(coursesname)))
            res = 'Adding Courses Success!'
            mydb.commit()
        except:
            res = 'Some Database Error'
        print(res)
        return res
    return res

def getAllUnassignedUsers():
    cursor = mydb.cursor()
    idroles = getRoleIdByName('none')
    query_string = "SELECT * FROM users WHERE idroles = %s";
    cursor.execute(query_string,(idroles,))
    users = cursor.fetchall()
    print('Courses Existing are ', users)
    return users

def accountRoleApproval(notnonedata):
    cursor = mydb.cursor()
    for i in range(0, len(notnonedata)):
        idroles = getRoleIdByName(notnonedata[i][1])
        try:
            query_string = "UPDATE users SET idroles = %s WHERE idusers = %s"
            cursor.execute(query_string, (str(idroles), str(notnonedata[i][0]),))
            mydb.commit()
        except ValueError:
            print('Database error, not updated!')
            return 'Some Database Error'
    res = 'Roles Assigned Success!'
    print(res)
    return res

def createNewUser(name,emailid,password,salt):
    res = 'Email-id already exists!'
    cursor = mydb.cursor()
    query_string = "SELECT * FROM users WHERE emailid = %s";
    cursor.execute(query_string,(emailid,))
    emchk = cursor.fetchall()
    if(len(emchk) == 0):
        query_string = "INSERT INTO users(name,emailid,password,salt) VALUES (%s ,%s, %s, %s)"
        try:
            cursor.execute(query_string, (str(name),str(emailid),str(password),str(salt)))
            res = 'Adding user Success!'
            mydb.commit()
        except:
            res = 'Some Database Error'
    print(res)
    return res

def getUnassignedCourses():
    # idcourses = getUserCourseIDs(idusers = idusers)
    cursor = mydb.cursor()
    idfaculty = getRoleIdByName("faculty")
    query_string1 = "SELECT a.idcourses FROM courses as a " #NOT IN
    query_string3 = "SELECT idusers FROM users WHERE idroles = '"+str(idfaculty)+"'";
    query_string2 = "SELECT b.idcourses FROM userscourses as b WHERE idusers IN ("+query_string3+")"
    cursor.execute(query_string1)
    unassignedcourseids = cursor.fetchall()
    print('All Faculty idusers: ',unassignedcourseids)

    query_string = query_string1+" WHERE a.idcourses NOT IN ("+query_string2+")"
    cursor.execute(query_string)
    unassignedcourseids = cursor.fetchall()
    # print('ID courses ',idcourses)
    coursesidname = []
    # print('idres ',idresources,' idrole',idroles)
    for i in unassignedcourseids:
        query_string = "SELECT coursesname FROM courses WHERE idcourses = %s"
        cursor.execute(query_string, (i[0],))
        data = cursor.fetchall()
        coursesidname.append([i[0], data[0][0]])
    return coursesidname


def getNotAssignedUsersNoCourses(rolename):

    idroles = getRoleIdByName(rolename)
    cursor = mydb.cursor()

    query_string1 = "SELECT a.idusers FROM users as a WHERE idroles = "+str(idroles)
    cursor.execute(query_string1)
    data = cursor.fetchall()
    return data

