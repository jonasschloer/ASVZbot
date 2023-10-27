import time
import datetime
from selenium import webdriver
from pathlib import Path
import json

'''
Kondi
Irchel
Today
18:15
'''


def settings():
    # open settings
    global NameID, FacilityID, LoginData, headless

    # !!!!! Somehow, when you run this script a compiler, you need to use the following line instead.
    # with open('{}'.format(Path().absolute() / 'ASVZ Bot' / 'settings.txt'), 'r') as f:

    # !!! If you run from batch, only this one works
    try:
        with open("settings_local.txt") as f:
            lines = f.readlines()
            NameID = json.loads(lines[1])
            FacilityID = json.loads(lines[3])
            LoginData = json.loads(lines[5])
            headless = not ('True' == lines[7])
    except FileNotFoundError:
        with open("settings.txt") as f:
            lines = f.readlines()
            NameID = json.loads(lines[1])
            FacilityID = json.loads(lines[3])
            LoginData = json.loads(lines[5])
            headless = not ('True' == lines[7])


def read():
    # read input data
    global sport, facility, date, Time

    keys = "".join(x + ", " for x in list(NameID.keys()))
    print(f"\x1b[37mEnter Sport: {keys[:-2]}", "\x1b[32m")
    sport = input()

    keys = "".join(x + ", " for x in list(FacilityID.keys()))
    print(f"\x1b[37mEnter Facility: {keys[:-2]}", "\x1b[32m")
    facility = input()

    now = datetime.datetime.now()
    print("\x1b[37mEnter Date:", '"Today,"', '"Tomorrow"', "or YYYY-MM-DD", "\x1b[32m")
    date_input = input()
    if (date_input == "Today"):
        date = str(now.date())
    elif (date_input == "Tomorrow"):
        date = str((now + datetime.timedelta(days=1)).date())
    else:
        date = date_input

    print("\x1b[37mEnter Time, HH:MM", "\x1b[32m")
    Time = input()


class WindowsInhibitor:
    '''Prevent OS sleep/hibernate in windows; code from:
    https://github.com/h3llrais3r/Deluge-PreventSuspendPlus/blob/master/preventsuspendplus/core.py
    API documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx'''
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        pass

    def inhibit(self):
        import ctypes
        print("Preventing Windows from going to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS | WindowsInhibitor.ES_SYSTEM_REQUIRED)

    def uninhibit(self):
        import ctypes
        print("Allowing Windows to go to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS)


class Class:
    def __init__(self, sport, facility, date, time):
        # pretty obvious what this means
        self.sport = sport
        self.facility = facility
        self.date = date
        self.time = time

    # Beispiel https://asvz.ch/426-sportfahrplan?f[0]=sport:122920&f[1]=facility:45577&date=2023-02-15%2013:30
    def getURL(self):
        # find executable and open Edge browser
        global web
        # path = '{}'.format(Path().absolute() / 'ASVZ Bot' / 'msedgedriver.exe') # use this for running in VSCode
        path = '{}'.format(Path().absolute() / 'msedgedriver.exe')  # use this for running .bat file
        options = webdriver.edge.options.Options()
        options.add_argument('log-level=2')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if (headless):
            options.add_argument("--headless")
        web = webdriver.Edge(executable_path=path, options=options)

        url = f"https://asvz.ch/426-sportfahrplan?f[0]=sport:{NameID[self.sport]}&date={self.date}%20{self.time}&f[1]=facility:{FacilityID[self.facility]}"
        print(f"\x1b[32mOpening {url}", "\x1b[34m")
        # Search for lesson
        web.get(url)
        time.sleep(1)

        # return link to first earch result
        lection = web.find_element(by="xpath", value='//*[@id="block-asvz-next-content"]/div/div/div[2]/div[2]/div[1]/div/ul/li/a')
        self.url = str(lection.get_attribute('href'))
        lesson_name = web.find_element(by="css selector", value="div.teaser-list-calendar__day:nth-child(1) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1) > div:nth-child(2) > div:nth-child(1) > h4:nth-child(1) > span:nth-child(1)").text
        lesson_date = web.find_element(by="css selector", value="div.teaser-list-calendar__day:nth-child(1) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1) > div:nth-child(1) > div:nth-child(1)").text
        lesson_location = web.find_element(by="css selector", value="div.teaser-list-calendar__day:nth-child(1) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)").text
        print(f"\x1b[32mFound {lesson_name}, {lesson_date} at {lesson_location}. URL: {self.url}", "\x1b[34m")

    def checkLogin(self):
        # check if already logged in. Not really necessary
        web.get(self.url)
        if (web.find_element(by="css selector", value=".alert").text != "Du musst dich einloggen, bevor du dich einschreiben kannst."):
            print("\x1b[32mAlready logged in", "\x1b[34m")
            return True
        return False

    def login(self):
        # logging in to SwitchAAI using credentials provided in "settings.txt". This might take a while because lots of redirecting
        print("\x1b[32mLogging in to SwitchAAI as", LoginData["username"] + ".", "This might take a few seconds.", "\x1b[34m")
        if (web.current_url != self.url):
            web.get(self.url)
            time.sleep(1)

        time.sleep(0.5)
        web.find_element(by="xpath", value="/html/body/app-root/div/div[2]/app-lesson-details/div/div/app-lessons-enrollment-button/button").click()
        time.sleep(1)

        web.find_element(by="xpath", value="//*[@id=" + '"collapse_switch"' + "]/div/form/div/p/button").click()
        # web.find_element(by="xpath", value="/html/body/div[1]/div[5]/div[1]/div/div[2]/div/div/form/div/p/button").click()
        time.sleep(3)

        ETHSelect = web.find_element(by="xpath", value="//*[@id=" + '"userIdPSelection_iddtext"' + "]")
        ETHSelect.click()
        time.sleep(.2)
        ETHSelect.send_keys("ETH Zürich")
        time.sleep(.5)
        web.find_element(by="xpath", value="/html/body/div/div/div[2]/form/div/div[1]/input").click()
        time.sleep(.5)

        user = web.find_element(by="xpath", value=("//*[@id=" + '"username"' + "]"))  # //*[@id="username"]
        user.send_keys(LoginData["username"])
        pw = web.find_element(by="xpath", value=("//*[@id=" + '"password"' + "]"))  # //*[@id="password"]
        pw.send_keys(LoginData["password"])
        web.find_element(by="xpath", value="/html/body/div[2]/main/section/div[2]/div[2]/form/div[5]/button").click()

        # wait until ASVZ page has loaded since this might take a while
        while (web.current_url != self.url):
            time.sleep(0.5)
        time.sleep(1.5)
        return True

    def full(self):
        # check if lesson is full
        # full = WebDriverWait(webdriver.Edge(), 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".badge")))
        # full.get_attribute("text")

        try:
            full = web.find_element(by="css selector", value=".badge").text
            if not (full == "0"):
                return False
            else:
                web.get(self.url)
                time.sleep(0.5)
                return True
        except Exception:
            # print(r"¯\_(ツ)_/¯         ")
            time.sleep(0.2)
            if web.current_url != self.url:
                web.get(self.url)
            return True

    def checkSleep(self):
        # check time until enrollment opens and go to sleep if longer than 1min before. Starts to try to login at least 30s before opening
        time.sleep(0.5)
        now = datetime.datetime.now()
        enroll_time = ""
        # find the element displaying enroll time (either child 10 or 11, depending if the name of the trainer is given)
        try: 
            enroll_element = web.find_element(by="css selector", value="#eventDetails > div > div.col-sm-4 > div > div.card-body.event-properties > app-lesson-properties-display > dl:nth-child(11) > dd").text
            if any(char.isdigit() for char in enroll_element):
                enroll_time = enroll_element[4:20]
        except Exception:
            enroll_element = web.find_element(by="css selector", value="#eventDetails > div > div.col-sm-4 > div > div.card-body.event-properties > app-lesson-properties-display > dl:nth-child(10) > dd").text[4:20]
            if any(char.isdigit() for char in enroll_element):
                enroll_time = enroll_element[4:20]
        # print(enroll_time)
        mon, day = 2, 2
        if (enroll_time[3] == "0"):
            mon = enroll_time[4:5]
        else:
            mon = enroll_time[3:5]
        if (enroll_time[0] == "0"):
            day = enroll_time[1]
        else:
            day = enroll_time[:2]
        # print(int(enroll_time[6:10]), int(mon), int(day), int(enroll_time[11:13]), int(enroll_time[14:16]))
        enroll_date = datetime.datetime(int(enroll_time[6:10]), int(mon), int(day), int(enroll_time[11:13]), int(enroll_time[14:16]))
        if (enroll_date > (now + datetime.timedelta(seconds=30))):
            seconds = (enroll_date - (now + datetime.timedelta(seconds=30))).total_seconds()
            print(f"\x1b[32mEnroll date {enroll_date}. Sleeping for {seconds} seconds until 30s before", "\x1b[34m")
            time.sleep(seconds)

    def enroll(self):
        # enroll to class
        print("\x1b[32mEnrolling       ", "\x1b[34m")

        # prevent de-registration
        if (web.find_element(by="css selector", value="#btnRegister").text == "EINSCHREIBUNG FÜR LEKTION ENTFERNEN"):
            print("\x1b[32mAlready enrolled   ", "\x1b[34m")
            return True

        # try enrolling
        i = 0
        # //*[@id="btnRegister"]

        while (True):
            enroll_button = web.find_element(by="xpath", value="//*[@id=" + '"btnRegister"' + "]")
            try:
                enroll_button.click()
                print("\x1b[32mRegistration Successful!", "\x1b[34m")
                break
            except Exception:
                print("\x1b[32mClicking" + (i % 4) * ".", "\x1b[34m", end="\r", flush=True)
                i += 1
                if (i > 500):
                    print("\x1b[32mSomething went horribly wrong :(", "\x1b[34m")
                    break

    def register(self):
        # This manages the whole process!

        # first, find the right URL
        print(f"\x1b[32mSearching for {self.sport} at {self.facility} on {self.date} at {self.time}", "\x1b[34m")
        Sport.getURL()

        osSleep = WindowsInhibitor()
        osSleep.inhibit()

        # Log in and print error if not working
        if not (Sport.login()):
            print("\x1b[32mError Logging in", "\x1b[34m")
            return False
        print("\x1b[32mLogin Successful", "\x1b[34m")

        # Check if far in future and wait until 30s before
        Sport.checkSleep()

        # As long as lesson is full, refresh page
        i = 0
        while (Sport.full()):
            print("\x1b[32mFull, refreshing" + i * ".", "\x1b[34m", end="\r", flush=True)
            i = (i + 1) % 4
            if web.current_url != self.url:
                web.get(self.url)

        # enroll!
        Sport.enroll()
        osSleep.uninhibit()


if __name__ == "__main__":

    settings()
    read()
    Sport = Class(sport, facility, date, Time)
    # Sport = Class('Fitness', 'Irchel', '2023-02-28', '15:30') # Example for quick debugging
    Sport.register()
