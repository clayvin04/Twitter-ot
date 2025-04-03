from seleniumbase import BaseCase
import pandas as pd



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


class Data(BaseCase):
    
    def setUp(self):
       
        super(Data, self).setUp()
        self.followers = 0
        self.following = 0
        self.tweets = 0
        self.posts = 0
        self.username = info.username if info.username else ""
        self.name = ""
        self.profile_pic_url = ""
        self.bio = ""
        self.url = info.url if info.url else ""

    def test_log_in(self, username="", password=""):
        
        login_url = 'https://x.com/i/flow/login?lang=en'
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
                self.type('//input[@name="text"]', username)
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
        
        following_data = []
        followers_data = []
        #print(self.following)
        for i in range(self.following):
            data = self.find_elements('div[data-testid="cellInnerDiv"]')
            following_data.append(data)
        print(following_data.text)