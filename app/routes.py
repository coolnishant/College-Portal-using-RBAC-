from flask import render_template, flash, redirect, request, session, url_for

from app import app
from app.databaseconn import mydb
from app.utility import getPermissions, getOwnMarks, getMarks, getNotAssignedUsers, getAllExistingCourses, addNewCourse, \
    getRole, getAllUnassignedUsers, accountRoleApproval, createNewUser, getSalt, getUnassignedCourses, \
    getNotAssignedUsersNoCourses
from app.utility import getResourceId,getStudentInCourse
from app.utility import getUserCoursesIdName
from app.utility import getUserCoursesMarks,addStudentInCourse
from app.utility import verifyPermissions,checkUserCourse
from app.utility import getTAInCourse, addUserInCourse,removeUserFromCourse
from app.utility import getAllMarksFromCourse, insertEditedMarksInCourse
from app.utility import deleteStudentMarks

from app.forms import LoginForm, AddStudentForm, AddTAForm, RemoveTAForm, AddEditStudentMarksForm, \
    DeleteStudentMarksForm, CreatingCoursesForm, AccountApprovalForm, SignupForm, AssignFacultyCourseForm


# @app.route('/')
# @app.route('/index')
def index():
    user = {'username': 'Miguel', 'password': 'mypass'}
    return render_template('index.html', title='Home', user=user)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # session.pop('username')
    session.pop('userdata')
    session.pop('idusers')
    session.pop('role')
    # session['permissionon' + resourcename] = permissionon
    session.pop('allpermissionon')

    return redirect(url_for('login'))

# @app.route('/')
def login2():
    form = LoginForm()
    if form.validate_on_submit():
        return render_template('student.html', title="Student")
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        # print('here')
        mycursor = mydb.cursor()

        # mycursor.execute("SHOW TABLES")
        mycursor.execute("SELECT * FROM user")
        data = []
        for x in mycursor:
            data.append(x)
        return render_template('student.html', title="Student", data=data)
    else:
        return render_template('index.html', title='Sign-Up/Login Form', form=form)


# @app.route('/', methods = ['GET', 'POST'])
def loginseperate():
    form = LoginForm()
    # print('here'+request.method)
    if request.method == 'POST':
        print(form.validate())
        if form.validate_on_submit():
            print('here3')
            cursor = mydb.cursor()
            emailid = form.username.data
            password = form.password.data
            password = password.encode('utf-8')
            import hashlib, uuid
            salt = uuid.uuid4().hex
            salt = salt.encode('utf-8')
            hashed_password = hashlib.sha512(password + salt).hexdigest()

            print(emailid, hashed_password)
            query_string = "SELECT idusers, name, emailid, idroles FROM users WHERE emailid = %s AND password = %s"
            cursor.execute(query_string, (emailid, hashed_password,))
            data = cursor.fetchall()

            print('data len: ', len(data))

            if len(data) == 1:
                idusers = data[0][0]
                name = data[0][1]
                emailid = data[0][2]
                idroles = data[0][3]
                session['idusers'] = idusers
                # TODO not assigned users role manage

                role = getRole(idroles)

                role = role[0]

                session['role'] = role

                # specify resource name
                resourcename = 'courses'
                resourcename1 = 'faculty'
                resourcename2 = 'ta'
                resourcename3 = 'student'

                operationsconstraints = getPermissions(idroles=idroles, resourcename=resourcename)
                operationsconstraints1 = getPermissions(idroles=idroles, resourcename=resourcename1)
                operationsconstraints2 = getPermissions(idroles=idroles, resourcename=resourcename2)
                operationsconstraints3 = getPermissions(idroles=idroles, resourcename=resourcename3)

                allpermissionon = {}
                permissionon = {}
                permissionon['resourcename'] = resourcename
                permissionon['permissions'] = operationsconstraints
                allpermissionon[getResourceId(resourcename)] = [permissionon]

                permissionon = {}
                permissionon['resourcename'] = resourcename1
                permissionon['permissions'] = operationsconstraints1
                allpermissionon[getResourceId(resourcename1)] = [permissionon]

                permissionon = {}
                permissionon['resourcename'] = resourcename2
                permissionon['permissions'] = operationsconstraints2
                allpermissionon[getResourceId(resourcename2)] = [permissionon]

                permissionon = {}
                permissionon['resourcename'] = resourcename3
                permissionon['permissions'] = operationsconstraints3
                allpermissionon[getResourceId(resourcename3)] = [permissionon]
                # permissionon  = [getResourceId(resourcename), resourcename, operationsconstraints]

                session['allpermissionon'] = allpermissionon
                print(allpermissionon)
                if (role == 'student'):

                    query_string = "SELECT idusers, name, emailid, idroles FROM users WHERE emailid = %s AND password = %s"
                    cursor.execute(query_string, (emailid, hashed_password,))
                    data = cursor.fetchall()

                    courses = getUserCoursesIdName(idusers=idusers)

                    print(courses[0])

                    for i in courses:
                        data.append([i[0], i[1], getUserCoursesMarks(idusers, i[0])])

                    return render_template('student.html', title="Student", data=data, form=form)
                elif role == 'ta':
                    return render_template('student.html', title="Student", data=data, form=form)
                # cursor.execute("SELECT * FROM users")
                #
                # data = []
                # for x in cursor:
                #     data.append(x)
        else:
            print('here2')
            print(form.password.data)
            flash('All fields are required.')
            return render_template('index.html', form=form)
    return render_template('index.html', form=form)



@app.route('/login', methods=['GET','POST'])
def login():
    print('login')
    form2 = SignupForm()
    form = LoginForm()
    error = ''
    if request.method == 'POST':
        print('form1: ',form.validate())
        if form.submit.data and form.validate_on_submit():
            # print('here3')
            error = None
            cursor = mydb.cursor()
            emailid = form.username.data
            password = form.password.data

            # password = password.encode('utf-8')
            import hashlib, uuid

            # salt = uuid.uuid4().hex
            # print('salt: ',salt)
            salt = getSalt(emailid)
            # print(salt)
            # salt = salt.encode('utf-8')
            hashed_password = hashlib.sha256((salt+password).encode('utf-8')).hexdigest()
            # print(salt)
            print(emailid, hashed_password)
            query_string = "SELECT idusers, name, emailid, idroles FROM users WHERE emailid = %s AND password = %s"
            cursor.execute(query_string, (emailid, hashed_password,))
            data = cursor.fetchall()

            print('data len: ', len(data))

            if len(data) == 1:
                userdata = {}
                idusers = userdata['idusers'] = data[0][0]
                userdata['name'] = data[0][1]
                userdata['emailid'] = data[0][2]
                idroles = data[0][3]
                session['userdata'] = userdata
                session['idusers'] = idusers
                # DONE not assigned users role manage

                role = getRole(idroles)

                role = role[0]

                session['role'] = role

                # specify resource name
                # specify resource name
                resourcename = 'courses'
                resourcename1 = 'faculty'
                resourcename2 = 'ta'
                resourcename3 = 'student'

                if (role == 'none'):
                    permissionon = {}
                    permissionon['idresources'] = 0
                    permissionon['resourcename'] = resourcename
                    permissionon['permissions'] = 'none'
                    session['permissionon' + resourcename] = permissionon

                    error = 'You are not an assigned user :). Contact Admin!'
                    return render_template('index.html', title="Login Page!", form=form, form2=form2, error=error)

                operationsconstraints = getPermissions(idroles=idroles, resourcename=resourcename)
                operationsconstraints1 = getPermissions(idroles=idroles, resourcename=resourcename1)
                operationsconstraints2 = getPermissions(idroles=idroles, resourcename=resourcename2)
                operationsconstraints3 = getPermissions(idroles=idroles, resourcename=resourcename3)

                allpermissionon = {}
                permissionon = {}
                permissionon['idresources'] = getResourceId(resourcename)
                permissionon['permissions'] = operationsconstraints
                allpermissionon[resourcename] = permissionon

                permissionon = {}
                permissionon['idresources'] = getResourceId(resourcename1)
                permissionon['permissions'] = operationsconstraints1
                allpermissionon[resourcename1] = permissionon

                permissionon = {}
                permissionon['idresources'] = getResourceId(resourcename2)
                permissionon['permissions'] = operationsconstraints2
                allpermissionon[resourcename2] = permissionon

                permissionon = {}
                permissionon['idresources'] = getResourceId(resourcename3)
                permissionon['permissions'] = operationsconstraints3
                allpermissionon[resourcename3] = permissionon
                # permissionon  = [getResourceId(resourcename), resourcename, operationsconstraints]

                session['allpermissionon'] = allpermissionon
                print(allpermissionon)

                # return redirect(url_for('onepage'))
                return render_template('onepage.html', title="One Page")

            else:
                error = 'Invalid Credentials! Try Again!'
                # return render_template('index.html',  form2=form2, error=error, form=form)
        else:
            print('here3')
            print(form.password.data)
            flash('All fields are required.')
            error = 'Invalid Credentials! Try Again!'
    return render_template('index.html', error=error, form=form, form2=form2 )

@app.route('/signup', methods=['GET','POST'])
def signup():
    print('signup')
    form2 = SignupForm()
    form = LoginForm()
    error = ''

    if request.method == 'POST':
        print(form2.validate())
        if form2.submit.data and form2.validate_on_submit():
            name = form2.username.data
            emailid = form2.emailid.data
            password = form2.password.data

            # password = password.encode('utf-8')
            import hashlib, uuid
            salt = uuid.uuid4().hex
            # salt = salt.encode('utf-8')
            hashed_password = hashlib.sha256((salt+password ).encode('utf-8')).hexdigest()

            print(name,emailid,hashed_password)
            if(name and emailid and hashed_password):
                error = createNewUser(name,emailid,hashed_password,salt)
                # name=name
            else:
                error = "Don't have sufficient field data!"
    return render_template('index.html', form2=form2 , form=form, error = error)

@app.route('/', methods=['GET','POST'])
def index():
    print('index')
    form2 = SignupForm()
    form = LoginForm()
    error =''
    return render_template('index.html', error=error, form=form, form2=form2)


@app.route('/onepage')
def onepage():
    print('one page')

    # resourcename = 'courses'
    # print(session['permissionon' + resourcename])

    # role = session['role']
    # # print(session[''])
    # # if (role == 'student'):
    # idusers = session['idusers']
    #
    # courses = getUserCoursesIdName(idusers=idusers)
    #
    # print(courses[0])
    # data = None
    #
    # for i in courses:
    #     data.append([i[0], i[1], getUserCoursesMarks(idusers, i[0])])

    # return render_template('student.html', title="Courses Page", data=data)
    return render_template('onepage.html')
    # return redirect(url_for('courses'))


@app.route('/courses')
def courses():
    print('courses')

    resourcename = 'courses'
    print(session['allpermissionon'])

    # role = session['role']
    # if (role == 'student'):
    idusers = session['idusers']

    courses = getUserCoursesIdName(idusers=idusers)

    # print(courses[0])
    data = []

    for i in courses:
        data.append([i[0], i[1]])

    print('data: ',data)
    # return render_template('student.html', title="Courses Page", data=data)
    return render_template('courses.html', data=data)
    # return render_template('onepage.html')


@app.route('/eachcourse')
def eachcourse():
    print('eachcourses')
    # TODO display list as view refined

    permissions = session['allpermissionon']
    todisplayresprm = [['student', 'write'], ['ta', 'update'], ['ta', 'update'],
                       ['courses', 'update'], ['courses', 'update']]

    # idusers = session['idusers']
    # resourcename = 'ta'
    # permissions = session['allpermissionon']
    # print(permissions)
    # checkusercourse = checkUserCourse(idusers, idcourses)
    # permupdate, constupdate = verifyPermissions(permissions, resourcename, 'update')
    # # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    # print('Read: ', permupdate, constupdate)

    todisplay = [False, False, False,False, False,True]
    k = 0
    print(todisplayresprm[1][1])
    for i in todisplayresprm:
        print('i is ',k)
        todisplay[k], const = verifyPermissions(permissions, i[0], i[1])

        if(todisplay[k]):
            todisplay[5] = False
        k = k + 1
    print('TO display: ',todisplay)


    idcourses = request.args.get('idcourses')
    print('Course id',idcourses)
    idusers = session['idusers']
    resourcename = 'courses'
    permissions = session['allpermissionon']
    print(permissions)
    #DONE do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):
        # read
    perm, const = verifyPermissions(permissions, resourcename, 'read')
    print(perm,const)
    data = []
    if(perm):
        if(const.__contains__('self')):
            if (const.__contains__('ownmarks')):
                tdata = getOwnMarks(idusers,idcourses)
                data = []
                for i in tdata:
                    j = i[1]
                    if (i[1] == -1):
                        j = 'NA'
                    data.append([i[0], j])
            elif (const.__contains__('marks')):
                tdata = getMarks(idcourses)
                data = []
                for i in tdata:
                    j = i[1]
                    if (i[1] == -1):
                        j = 'NA'
                    data.append([i[0], j])
    else:
        data.append(['No data'])
    return render_template('eachcourse.html', data=data, idcourses = idcourses, todisplay=todisplay)

@app.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    addstudentform = AddStudentForm()
    print('addstudent')
    idcourses = request.args.get('idcourses')
    # idcourse = request.args.get('idcourses')
    if(idcourses == None):
        idcourses = str(request.form.getlist('idcourses')[0])

    print(idcourses)
    idusers = session['idusers']
    resourcename = 'student'
    permissions = session['allpermissionon']
    print(permissions)
    #DONE do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):
        # read
    checkusercourse = checkUserCourse(idusers, idcourses)
    permread, constread = verifyPermissions(permissions, resourcename, 'read')
    permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print(permread, constread)
    print(permwrite, constwrite)
    data = [['Permission Denied']]
    data2 = [['Permission Denied']]
    if (checkusercourse and permread and permwrite):
        if (constread.__contains__('self')):
            if (constread.__contains__('ownmarks')):
                data = [['Permission Denied']]
            elif (constread.__contains__('marks')):
                data = [['Permission Denied']]
            else:
                if request.method == 'POST':
                    # print('Validate: ',addstudentform.validate())
                    # if addstudentform.validate_on_submit():
                    chkbox_values = request.form.getlist('addstudentchkbox')
                    # data = []
                    # data.append(chkbox_values)
                # DONE insert in database
                    if len(chkbox_values)!=0:
                        print('check values: ',chkbox_values)
                        addStudentInCourse(idcourses,chkbox_values)
                data = getStudentInCourse(idcourses)
                data2 = getNotAssignedUsers(idcourses, 'student')
    return render_template('addstudent.html',data=data, data2=data2, addstudentform=addstudentform, idcourses=idcourses)
    # return render_template('onepage.html')


@app.route('/addta', methods=['GET', 'POST'])
def addta():
    addtaform = AddTAForm()
    print('addta')
    idcourses = request.args.get('idcourses')
    if(idcourses == None):
        idcourses = str(request.form.getlist('idcourses')[0])

    print(idcourses)
    idusers = session['idusers']
    resourcename = 'ta'
    permissions = session['allpermissionon']
    print(permissions)
    #TODO do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):

    checkusercourse = checkUserCourse(idusers, idcourses)
    permupdate, constupdate = verifyPermissions(permissions, resourcename, 'update')
    # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print('Read: ',permupdate, constupdate)
    # print('Write: ',permwrite, constwrite)
    data = [['Permission Denied']]
    data2 = [['Permission Denied']]
    if (checkusercourse and permupdate ):
        if (constupdate.__contains__('self')):
            if (constupdate.__contains__('ownmarks')):
                data = [['Permission Denied']]
            elif (constupdate.__contains__('marks')):
                data = [['Permission Denied']]
            else:
                if request.method == 'POST':
                    # print('Validate: ',addstudentform.validate())
                    # if addstudentform.validate_on_submit():
                    chkbox_values = request.form.getlist('addtachkbox')
                    # data = []
                    # data.append(chkbox_values)
                # DONE insert in database
                    if len(chkbox_values)!=0:
                        print('check values: ',chkbox_values)
                        addUserInCourse(idcourses,chkbox_values)
                data = getTAInCourse(idcourses,'ta')
                data2 = getNotAssignedUsers(idcourses, 'ta')
    return render_template('addta.html',data=data, data2=data2, addtaform=addtaform, idcourses=idcourses)
    # return render_template('onepage.html')

@app.route('/removeta', methods=['GET', 'POST'])
def removeta():
    removetaform = RemoveTAForm()
    print('removeta')
    idcourses = request.args.get('idcourses')
    # idcourse = request.args.get('idcourses')
    if(idcourses == None):
        idcourses = str(request.form.getlist('idcourses')[0])

    print(idcourses)
    idusers = session['idusers']
    resourcename = 'student'
    permissions = session['allpermissionon']
    print(permissions)
    #DONE do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):
        # read
    checkusercourse = checkUserCourse(idusers, idcourses)
    permread, constread = verifyPermissions(permissions, resourcename, 'read')
    permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print(permread, constread)
    print(permwrite, constwrite)
    data = [['Permission Denied']]
    # data2 = [['Permission Denied']]
    if (checkusercourse and permread and permwrite):
        if (constread.__contains__('self')):
            if (constread.__contains__('ownmarks')):
                data = [['Permission Denied']]
            elif (constread.__contains__('marks')):
                data = [['Permission Denied']]
            else:
                if request.method == 'POST':
                    # print('Validate: ',addstudentform.validate())
                    # if addstudentform.validate_on_submit():
                    chkbox_values = request.form.getlist('removetachkbox')
                    # data = []
                    # data.append(chkbox_values)
                # DONE insert in database
                    if len(chkbox_values)!=0:
                        print('check values: ',chkbox_values)
                        removeUserFromCourse(idcourses,chkbox_values)
                data = getTAInCourse(idcourses,'ta')
                # data2 = getNotAssignedUsers(idcourses, 'student')
    return render_template('removeta.html',data=data, removetaform=removetaform, idcourses=idcourses)
    # return render_template('onepage.html')


@app.route('/addeditstudentmarks', methods=['GET', 'POST'])
def addeditstudentmarkss():
    addeditstudentmarksform = AddEditStudentMarksForm()
    print('addeditstudentmarks')
    idcourses = request.args.get('idcourses')
    # idcourse = request.args.get('idcourses')
    if(idcourses == None):
        idcourses = str(request.form.getlist('idcourses')[0])
    print(idcourses)
    idusers = session['idusers']
    resourcename = 'courses'
    permissions = session['allpermissionon']
    print(permissions)
    #DONE do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):
        # read
    checkusercourse = checkUserCourse(idusers, idcourses)
    permupdate, constupdate = verifyPermissions(permissions, resourcename, 'update')
    # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print(permupdate, constupdate)
    # print(permwrite, constwrite)
    data = [['Permission Denied']]
    # data2 = [['Permission Denied']]
    if (checkusercourse and permupdate):
        if (constupdate.__contains__('self')):
            if (constupdate.__contains__('ownmarks')):
                data = [['Permission Denied']]
            # elif (constupdate.__contains__('marks')):
            #     data = [['Permission Denied']]
            else:
                if request.method == 'POST':
                    # print('Validate: ',addstudentform.validate())
                    # if addstudentform.validate_on_submit():
                    addeditstudent = request.form.getlist('addeditstudentmarks')
                    # data = []
                    # data.append(addeditstudentmarks)
                # DONE insert in database
                    if len(addeditstudent)!=0:
                        idusers = request.form.getlist('idusers')
                        print('check values: ',idusers," ",addeditstudent)
                        insertEditedMarksInCourse(idcourses,idusers,addeditstudent)
                tdata = getAllMarksFromCourse(idcourses)
                data=[]
                for i in tdata:
                    j = i[1]
                    if(i[1] == -1):
                        j = 'NA'
                    data.append([i[0],j])
                # data2 = getNotAssignedUsers(idcourses, 'student')
    return render_template('addeditstudentmarks.html',data=data, form = addeditstudentmarksform,
                           idcourses=idcourses)
    # return render_template('onepage.html')


@app.route('/deletestudentmarks', methods=['GET', 'POST'])
def deletestudentmarks():
    deletestudentmarksform = DeleteStudentMarksForm()
    print('deletestudentmarks')
    idcourses = request.args.get('idcourses')
    # idcourse = request.args.get('idcourses')
    if(idcourses == None):
        idcourses = str(request.form.getlist('idcourses')[0])
    print(idcourses)
    idusers = session['idusers']
    resourcename = 'courses'
    permissions = session['allpermissionon']
    print(permissions)
    #TODO do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):
        # read
    checkusercourse = checkUserCourse(idusers, idcourses)
    permupdate, constupdate = verifyPermissions(permissions, resourcename, 'update')
    # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print(permupdate, constupdate)
    # print(permwrite, constwrite)
    data = [['Permission Denied']]
    # data2 = [['Permission Denied']]
    if (checkusercourse and permupdate):
        if (constupdate.__contains__('self')):
            if (constupdate.__contains__('ownmarks')):
                data = [['Permission Denied']]
            # elif (constupdate.__contains__('marks')):
            #     data = [['Permission Denied']]
            else:
                if request.method == 'POST':
                    # print('Validate: ',addstudentform.validate())
                    # if addstudentform.validate_on_submit():
                    chkbox_values = request.form.getlist('deletestudentmarkschkbox')
                    # data = []
                    # data.append(chkbox_values)
                # DONE insert in database
                    if len(chkbox_values)!=0:
                        print('check values: ',chkbox_values)
                        deleteStudentMarks(idcourses,chkbox_values)
                tdata = getAllMarksFromCourse(idcourses)
                data = []
                for i in tdata:
                    if(i[1] != -1):
                        data.append(i)
                # data2 = getNotAssignedUsers(idcourses, 'student')
    return render_template('deletestudentmarks.html',data=data, deletestudentmarksform=deletestudentmarksform, idcourses=idcourses)
    # return render_template('onepage.html')

########################DB Activity########################################


@app.route('/dbactivity')
def dbactivity():
    print('dbactivity')

    # idcourses = request.args.get('idcourses')
    # print('Course id',idcourses)

    idusers = session['idusers']
    resourcename = 'courses'
    permissions = session['allpermissionon']
    print(permissions)
    #TODO do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):
        # read
    perm, const = verifyPermissions(permissions, resourcename, 'create')
    print(perm,const)
    data = []
    # data2 = [['Permission Denied']]
    if (perm):
        data = ['Go on']

    return render_template('dbactivity.html', data=data)

@app.route('/creatingcourses', methods=['GET', 'POST'])
def creatingcourses():
    creatingcoursesform = CreatingCoursesForm()
    print('creatingcourses')

    idusers = session['idusers']
    resourcename = 'courses'
    permissions = session['allpermissionon']
    print(permissions)

    permcreate, constcreate = verifyPermissions(permissions, resourcename, 'create')
    print('Create Course: ',permcreate, constcreate)
    data = [['Permission Denied']]
    res = ''
    if (permcreate):
        if request.method == 'POST':
            # print('Validate: ',creatingcoursesform.validate())
            # if creatingcoursesform.validate_on_submit():

            idcourses = creatingcoursesform.idcourses.data
            coursesname = creatingcoursesform.coursename.data

        # DONE insert in database
            if len(idcourses) != 0 and len(coursesname) != 0 :
                print('Values Add New Course: ',idcourses, coursesname)
                res = addNewCourse(idcourses,coursesname)
        data = getAllExistingCourses()
    print('res: ',len(res))
    return render_template('creatingcourses.html',data=data, res = res, permcreate = permcreate, form=creatingcoursesform)
    # return render_template('onepage.html')


@app.route('/accountapproval', methods=['GET', 'POST'])
def accountapproval():
    accountapprovalform = AccountApprovalForm()
    print('accountapproval')

    resourcename = 'courses'
    permissions = session['allpermissionon']
    print(permissions)

    permcreate, constcreate = verifyPermissions(permissions, resourcename, 'create')
    # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print(permcreate, constcreate)
    # print(permwrite, constwrite)
    data = [['Permission Denied']]
    # data2 = [['Permission Denied']]
    res= ''
    if (permcreate):
        if request.method == 'POST':
            # print('Validate: ',addstudentform.validate())
            # if addstudentform.validate_on_submit():
            idusers = request.form.getlist('idusers')
            # print(idusers[0])
            notnonedata2 = []
            for i in idusers:
                select = request.form.get('comp_select_'+i)
                if select != 'none':
                    notnonedata2.append([i,select])
                    # print(select)

        # DONE insert in database
            if len(notnonedata2) != 0:
                print('check values: ',notnonedata2)
                res = accountRoleApproval(notnonedata2)
            else:
                res = 'No Role Selected for updating!'
        data = getAllUnassignedUsers()

    return render_template('accountapproval.html',data=data, perm = permcreate, res =res, form=accountapprovalform)
    # return render_template('onepage.html')


@app.route('/unassignedcourses', methods=['GET', 'POST'])
def unassignedcourses():
    print('unassignedcourses')
    resourcename = 'courses'
    print(session['allpermissionon'])

    # role = session['role']
    # if (role == 'student'):
    # idusers = session['idusers']

    courses = getUnassignedCourses()

    # print(courses[0])
    data = []

    for i in courses:
        data.append([i[0], i[1]])

    print('data: ', data)
    # return render_template('student.html', title="Courses Page", data=data)
    return render_template('unassignedcourses.html', data=data)


@app.route('/assignfacultycourse', methods=['GET', 'POST'])
def assignfacultycourse():
    print('assignfacultycourse')
    assignfacultycourseform = AssignFacultyCourseForm()
    idcourses = request.args.get('idcourses')
    print(request.form.getlist('idcourses'))
    if (idcourses == None):
        idcourses = str(request.form.getlist('idcourses')[0])

    print(idcourses)
    # idusers = session['idusers']
    resourcename = 'faculty'
    permissions = session['allpermissionon']
    print(permissions)
    # TODO do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):

    permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print('Write: ', permwrite, constwrite)
    # print('Write: ',permwrite, constwrite)
    data = [['Permission Denied']]
    data2 = [['Permission Denied']]
    if (permwrite):
        if (constwrite.__contains__('self')):
            if request.method == 'POST':
                # print('Validate: ',addstudentform.validate())
                # if addstudentform.validate_on_submit():
                chkbox_values = request.form.getlist('addtachkbox')
                # data = []
                # data.append(chkbox_values)
                # DONE insert in database
                if len(chkbox_values) != 0:
                    print('check values: ', chkbox_values)
                    addUserInCourse(idcourses, chkbox_values)
                    data = ['Go on']
                    return render_template('dbactivity.html', data=data)
            data2 = getNotAssignedUsersNoCourses('faculty')
            # print(data2)
    return render_template('assignfacultycourse.html', data2=data2, permwrite=permwrite,
                           assignfacultycourseform=assignfacultycourseform, idcourses=idcourses)
    # return render_template('onepage.html')


@app.route('/assignfacultyC', methods=['GET', 'POST'])
def assignfacultyC():
    print('assignfacultyC')
    # idusers = session['idusers']
    resourcename = 'faculty'
    permissions = session['allpermissionon']
    print(permissions)
    # TODO do all read write here on permission check
    # if (permissions['resourcename'] == resourcename):

    permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    # permwrite, constwrite = verifyPermissions(permissions, resourcename, 'write')
    print('Write: ', permwrite, constwrite)
    # print('Write: ',permwrite, constwrite)
    data = [['Permission Denied']]
    data2 = [['Permission Denied']]
    if (permwrite):
        if (constwrite.__contains__('self')):
            if request.method == 'POST':
                # print('Validate: ',addstudentform.validate())
                # if addstudentform.validate_on_submit():
                chkbox_values = request.form.getlist('addtachkbox')
                # data = []
                # data.append(chkbox_values)
                # DONE insert in database
                if len(chkbox_values) != 0:
                    idcourses = str(request.form.getlist('idcourses')[0])
                    print(idcourses)
                    print('check values: ', chkbox_values)
                    addUserInCourse(idcourses, chkbox_values)
                    redirect('unassignedcourses.html')

if __name__ == '__main__':
    app.run(debug=True)
