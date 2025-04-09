from seleniumbase import BaseCase
import pandas as pd
from test_my_script import Write_tweets, unfollo,rmove_followers,ask_name
from unittest.mock import patch


class Info:
    
    def __init__(self):
        self.username = ""
        self.password = ""
        self.scrape = ""
        self.url = ""

    # Check if this is a Twitter link
    def test_validate_twitter_url(self, url):
        valid_url = "https://x.com"
        
        if not url.startswith(valid_url) or url == valid_url:
            raise ValueError("Invalid Twitter link")
        
        parts = url[len(valid_url):].strip("/").split("/")
        if parts:
            self.username = parts[0]  # Extract username
            return True
        
        raise ValueError("Invalid Twitter link format")

    
    # Get account by username
    def test_validate_username_or_scrape(self, username=None, scrape=None):
        valid_url = "https://x.com"

        if not username and not scrape:
            raise ValueError("You must pass at least one argument")

        target = username if username else scrape  # Select input
        target = target.strip()  # Remove spaces from start and end

        if len(target) <= 1 or " " in target:
            raise ValueError("Invalid username!")

        if valid_url in target:
            return False  # URL is not allowed

        if username:
            self.username = target
            self.url = f"{valid_url}/{self.username}"
        else:
            self.scrape = target

        return True
    # Get Twitter account url 
    
    def test_get_full_path(self, url):
        if self.test_validate_twitter_url(url):
            self.url = url
            return True
        
        raise Exception('Something went wrong')
    
    def test_validate_login(self, username, password):
        if not self.test_validate_username_or_scrape(username):
            raise ValueError("Invalid username")

        if not password or len(password) <= 3:
            raise ValueError("Password must be at least 4 characters long")

        self.password = password
        return True
    



info = Info()
"""
# test Info
try:
    print(info.test_validate_twitter_url("https://x.com/user123"))  # True
except Exception as e:
    print(f"Error: {e}")


try:
    print(info.test_validate_username_or_scrape(username=" validUser "))  # True
except Exception as e:
    print(f"Error: {e}")


try:
    print(info.test_validate_login("validUser", "strongPass"))  # True
except Exception as e:
    print(f"Error: {e}")
"""

class Data(BaseCase):
    
    def setUp(self):
       
        super(Data, self).setUp()
        self.followers = 0
        self.following = 0
        self.tweets = 0
        self.posts = 0
        self.gmail = ""
        self.name = ""
        self.username = info.username if info.username else ""
        self.name_followers = ""
        self.name_following = ""
        
        self.profile_pic_url = ""
        self.bio = ""
        self.url = info.url if info.url else ""
        self.name = ask_name()
    def test_log_in(self, username="", password="", gmail = ""):
        
        login_url = 'https://x.com/i/flow/login'
        self.open(login_url)

        # Improved Login Validation
        try:
            login_valid = info.test_validate_login(username, password)
            if not login_valid:
                raise ValueError(" Username or Password is incorrect. Please try again.")
        except AttributeError:
            raise ValueError(" Login validation function not found! Check `info` class implementation.")
        except Exception as e:
            raise ValueError(f" Unexpected error during login validation: {e}")

        try:
            
            self.type("input[name='text']", username)
            self.click('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]')
            self.sleep(3)

            
            if self.is_text_visible("Enter your phone number or username"):
                self.type('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input', gmail)
                self.click('//button[@data-testid="ocfEnterTextNextButton"]')
                self.sleep(5)
                
            
            self.type("input[name='password']", password)
            self.click('/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button')
            self.sleep(5)

            
            if not self.assert_element_present("a[data-testid='AppTabBar_Home_Link']"):
                raise ValueError(" Login failed. Check credentials or handle additional verification.")
    
        except Exception as e:
            raise Exception(f" Login failed! Error: {e}")

        print(" Login Successful!")
    
    
    def test_account(self):
        self.test_log_in()
        self.sleep(5)
        
        try:
            self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/div/a')
            
            self.sleep(5)
        except Exception:
            print("error log test_account")
        
        try:
            # Find elements containing profile statistics
            following = self.find_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div[1]/div[1]/div[5]/div[1]/a')
            followers = self.find_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div[1]/div[1]/div[5]/div[2]/a')
            posts = self.find_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/div')
            
            # Extract and print stats text
            #print(followers.text + " " + following.text + " " + posts.text)
            
            # Convert and return the numeric values
            following_count = self.convert_number(following.text.split()[0])
            followers_count = self.convert_number(followers.text.split()[0])
            posts_count = self.convert_number(posts.text.split()[0])
            self.followers = followers_count
            self.following = following_count
            self.posts = posts_count
            
            print(f"following: {following_count}  followers  :{followers_count} posts: {posts_count}")
            
        except Exception as e:
            print(f"Error scraping profile stats: {e}")
            return None, None, None
            
    def convert_number(self, number):
        """
        Convert a number string with K or M suffix to its integer representation.
        
        Args:
            number: A string representing a number, possibly with K or M suffix
                (e.g., '10K', '1.5M')
                
        Returns:
            int: The converted integer value 
        """
        try:
            number = str(number).strip()
            
            if 'M' in number:
                value = float(number.replace('M', ''))
                return int(value * 1_000_000)
            
            elif 'K' in number:
                value = float(number.replace('K', ''))
                return int(value * 1_000)
            else:
                return int(float(number))
        except ValueError:
            return 0
    

    

    def test_data_following_followers(self):  
        self.test_account()  
        followers_names = []
        following_names = []  # Store unique names  
        self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div[1]/div[1]/div[5]/div[1]/a')  

        last_height = 0  
        attempts = 0  
        
        while len(following_names) < self.following:  
            # Use `BaseCase`'s find_elements method  
            name_elements = self.find_elements('span.css-1jxf684.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3', by='css selector')  

            for el in name_elements:  
                name = el.text.strip()  
                if name.startswith('@') and name not in following_names:  
                    following_names.append(name)  # Add unique @names only  

            # Scroll down to load more  
            self.execute_script("window.scrollBy(0, 1000);")  
            self.sleep(2)  # Reduce wait time for efficiency  

            # Check if new content is loading  
            new_height = self.execute_script("return document.body.scrollHeight")  
            if new_height == last_height:  
                attempts += 1  
                if attempts >= 3:  # Stop if no new content after 3 tries  
                    break  
            else:  
                attempts = 0  # Reset attempt counter  

            last_height = new_height  

        print(f"🔍 Extracted {len(following_names)} usernames starting with '@' out of {self.following}:")  
          
        self.name_following = following_names
        
        self.sleep(3)
        
        self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a')
        
        while len(followers_names) < self.followers:
            name_elements = self.find_elements('span.css-1jxf684.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3', by='css selector')  

            for el in name_elements:  
                name = el.text.strip()  
                if name.startswith('@') and name not in followers_names:  
                    followers_names.append(name)
            
            
             # Scroll down to load more  
            self.execute_script("window.scrollBy(0, 1000);")  
            self.sleep(2)   

            # Check if new content is loading  
            new_height = self.execute_script("return document.body.scrollHeight")  
            if new_height == last_height:  
                attempts += 1  
                if attempts >= 3:  # Stop if no new content after 3 tries  
                    break  
            else:  
                attempts = 0  # Reset attempt counter  

            last_height = new_height  

        print(f"🔍 Extracted {len(followers_names)} usernames starting with '@' out of {self.followers}:") 
        self.name_followers =followers_names
        
        
        
        self.test_load_account_data()
        
    
    
    def test_Write_tweets(self):
        self.test_log_in()
        
        name = Write_tweets()
        
        
        self.type("[data-testid='tweetTextarea_0']", name)
        self.sleep(5)
        self.click('/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button')
         
    
    
    
    
    
    def test_unfollo(self):
        self.test_log_in()
        
        self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/div/a')
        self.sleep(5)
        self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div[1]/div[1]/div[5]/div[1]/a')
        
        number = unfollo()
        n = int(number)
        self.sleep(3)
        for i in range(1, n+1):
            self.find_element(f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[{i}]/div/div/button/div/div[2]/div[1]/div[1]/div/div[2]/div/a/div/div/span")
            self.click(f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[{i}]/div/div/button/div/div[2]/div[1]/div[2]/button")
            self.sleep(10)
            
            self.click('/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/button[1]')
    
    def test_rmove_followers(self):
        self.test_log_in()
        self.sleep(5)
        self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/div/a')
        self.sleep(5)
        self.click('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div[1]/div[1]/div[5]/div[2]/a')
        self.click('/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a')
        
        number = rmove_followers()
        n = int(number)
        for i in range(1, n+1):
            self.find_element(f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[{i}]/div/div/button/div/div[2]/div[1]/div[1]/div/div[2]/div[1]/a/div/div/span")
            self.click(f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[{i}]/div/div/button/div/div[2]/div/div[2]/div[1]/button")
            self.sleep(10)
            
            self.click('/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/button[1]')
           
    def test_load_account_data(self):
        data_user = {
            'name' : self.name,
            'followers' : self.name_followers,
            'following': self.name_following,
            'posts' : self.posts
            
        }    
        
        df1 = pd.DataFrame(data_user)
        print(df1)
        

       