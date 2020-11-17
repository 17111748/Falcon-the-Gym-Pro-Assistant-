import sqlite3, datetime

#use rowid to get row id for an entry don't need to make a specific profile id?
class database(object):
    defaultWeight = 170
    defaultAge = 20
    def __init__(self,path):
        self.db = sqlite3.connect(path)
        self.cursor = self.db.cursor()
        applicationData = """CREATE TABLE IF NOT EXISTS application (lastProfile integer,
                                                                    FOREIGN KEY (lastProfile) REFERENCES profiles(profile_id));"""
        createProfile = """CREATE TABLE IF NOT EXISTS profiles (profile_id integer PRIMARY KEY, 
                                                                weight integer,
                                                                age integer);"""
        createWorkout = """CREATE TABLE IF NOT EXISTS workouts (duration real,
                                                                focus text,
                                                                timeStart timestamp,
                                                                timeEnd timestamp,
                                                                calories real,
                                                                avgHR integer,
                                                                profile integer,
                                                                FOREIGN KEY (profile) REFERENCES profiles(profile_id));"""
        self.cursor.execute(applicationData)
        self.cursor.execute(createProfile)
        self.cursor.execute(createWorkout)

        #make sure all 3 profiles exist, if not set to default values
        self.db.commit()
    def getProfile(self,profile):
        res = self.cursor.execute('SELECT * from profiles WHERE profile_id=?;',[profile]).fetchall()
        if(len(res)==0):
            entry = (profile,self.defaultWeight,self.defaultAge)
            cmd = 'INSERT INTO profiles VALUES (?,?,?);'
            self.cursor.execute(cmd,entry)
            self.db.commit()
            return entry
        return res[0]
    def updateProfile(self,profile,weight,age):
        #ensure that it exists
        self.getProfile(profile)
        sql = 'UPDATE profiles SET weight=? , age=? WHERE profile_id=?;'
        self.cursor.execute(sql,(weight,age,profile))
        self.db.commit()
        return True
    def getWorkouts(self,profile):
        sql = 'SELECT * from workouts WHERE profile=?;'
        res = self.cursor.execute(sql,(profile,)).fetchall()
        return res
    def addWorkout(self,focus,duration,timeStarted,timeEnded,calories,avgHR,profile):
        self.getProfile(profile)
        sql = """INSERT INTO workouts VALUES (?,?,?,?,?,?,?)"""
        self.cursor.execute(sql,(focus,duration,timeStarted,timeEnded,calories,avgHR,profile))
        self.db.commit()
    def getLastProfile(self):
        res = self.cursor.execute('SELECT * from application WHERE rowid=1;').fetchall()
        if(len(res)==0):
            cmd = 'INSERT INTO application VALUES (?);'
            self.cursor.execute(cmd,(1,))
            self.db.commit()
            return 1
        return res[0][0]
    def updateLastProfile(self,profile):
        #ensure that it exists
        self.getLastProfile()
        sql = 'UPDATE application SET lastProfile=? WHERE rowid=1;'
        self.cursor.execute(sql,(profile,))
        self.db.commit()
        return True


# testDatabase = database("falcon.db")
# for i in range(3):
#     testDatabase.getProfile(i+1)
# print(testDatabase.getWorkouts(2))
# testDatabase.addWorkout("core",10.5,datetime.datetime.now(),datetime.datetime.now(),180,170,1)
# print(testDatabase.getLastProfile())
# testDatabase.updateLastProfile(2)
