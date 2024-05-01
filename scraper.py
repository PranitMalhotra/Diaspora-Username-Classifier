#TODO have to make email and password as Env variables and ensure that they are 
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from tqdm import tqdm
import time

class HypeAuditorScraper:
    #public
    def scrape(self, gmail, password, india):
        # approach:
        # intialize browser-> login google account -> login hypeauditor -> get the IG usernames ->
        # (parse HTML -> next page)* 20 pages -> store in a pandas DataFrame

        URL = "https://hypeauditor.com/top-instagram-all-india/" if india == True else "https://hypeauditor.com/top-instagram-all-united-states/"

        self._initializeDriver()
        self._googleLogin(gmail, password)
        self._hypeauditorLogin()
        self.driver.get(URL)
        self.driver.implicitly_wait(1)

        df = pd.DataFrame()
        for i in tqdm(range(20)): # 20 pages for 1000 results
            df = pd.concat([df, self._fetchData()], axis = 0, ignore_index = True)
            if i < 20:
                self._nextPage(URL, i)
        self.driver.quit()

        return df

    #private
    def _initializeDriver(self):
        # adding appropriate chrome options
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("user_agent=DN")

        self.driver = uc.Chrome(options = chrome_options)

        self.driver.delete_all_cookies()
    
    #private
    def _googleLogin(self, gmail, password):
        self.driver.get("https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow")

        email_element = self.driver.find_element(By.TAG_NAME, "input") 
        email_element.send_keys(gmail, Keys.ENTER) # input gmail
        time.sleep(5)

        password_element = self.driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
        password_element.send_keys(password, Keys.ENTER) # input password
        time.sleep(10)

        self.driver.find_element(By.XPATH, '//*[@id = "yDmH0d"]/c-wiz/div/div[3]/div/div/div[2]/div/div/button').click() # press "continue"
        time.sleep(10)

    #private
    def _hypeauditorLogin(self):
        self.driver.get("https://hypeauditor.com/login/")
        time.sleep(10)

        self.driver.find_element(By.XPATH, '//*[@id="login-form-wrap"]/form[1]/div[1]/a').click() # press "use google login"
        time.sleep(10)

        self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/div/div/div/div/div/div[2]/div/div/div/form/span/section/div/div/div/div/ul/li[1]/div').click() # press which account to login
        time.sleep(10)

        self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[3]/div/div/div[2]/div/div/button').click() # press "continue"
        time.sleep(10)

    #private
    def _fetchData(self): # 50 results per page
        def objectToText(object_list, col_name): # .find_elements() method returns a list of objects
            return pd.DataFrame(data = [x.text for x in object_list], columns = [col_name])

        self.driver.implicitly_wait(1)
        username_list = objectToText(self.driver.find_elements(By.CLASS_NAME, "contributor__name-content"), "IG Username")
        return username_list

    #private
    def _nextPage(self, URL, i):
        time.sleep(1)

        page_no = i + 1
        page_url = URL + "?p=" + str(page_no)
        self.driver.get(page_url)

        time.sleep(2)
    