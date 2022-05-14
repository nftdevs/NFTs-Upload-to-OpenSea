from lib2to3.pgen2 import driver
import tkinter
import subprocess
from tkinter import *
from tkinter import filedialog
import os
import sys
import pickle
import time
import sys
import random
import string
import re

from numpy import pad
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from tkinter import *
from tkinter.ttk import *
from tkinter import ttk

root = Tk()
root.geometry('550x400')
root.title("NFTs Upload to OpenSea")
input_save_list = [None] * 11
main_directory = os.path.join(sys.path[0])
profile_directory = os.path.expanduser('~/Library/Application\ Support/Google/Chrome/Profile 2')
chrome = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
is_polygon = BooleanVar()
is_polygon.set(False)
skip_listing = BooleanVar()
skip_listing.set(False)
debug = BooleanVar()
debug.set(True)
headless = BooleanVar()
headless.set(False)
textVariable = tkinter.StringVar()
upload_path = StringVar()
force_patch = BooleanVar()
force_patch.set(True)


def open_chrome_profile():
    launch_string = chrome 
    if headless.get():
        launch_string += " --headless "
    launch_string += " --remote-debugging-port=9515 --user-data-dir=" + profile_directory
    return subprocess.Popen(
        [
            launch_string,
        ],
        shell=True,
    )

def save_file_path():
    return os.path.join(sys.path[0], "Save_file.cloud") 

# ask for directory on clicking button, changes button name.
def upload_folder_input():
    global upload_path
    upload_path = filedialog.askdirectory()
    upload_path_input.insert_text(upload_path)
    
class InputField:
    def __init__(self, label, row_io, column_io, pos, master=root, showVal=""):
        self.master = master
        self.input_field = Entry(self.master, show=showVal)
        self.input_field.label = Label(master, text=label)
        self.input_field.label.grid(row=row_io, column=column_io)
        self.input_field.grid(row=row_io, column=column_io + 1)
    
        try:
            with open(save_file_path(), "rb") as infile:
                new_dict = pickle.load(infile)
                self.insert_text(new_dict[pos])
        except FileNotFoundError:
            pass
        except IndexError:
            pass

    def insert_text(self, text):
        self.input_field.delete(0, "end")
        self.input_field.insert(0, '' if (text == None) else text)

    def save_inputs(self, pos):
        input_save_list[pos] = self.input_field.get()
        with open(save_file_path(), "wb") as outfile:
            pickle.dump(input_save_list, outfile)

###save inputs###
def save():
    #input_save_list.insert(0, upload_path)
    upload_path_input.save_inputs(0)
    collection_link_input.save_inputs(1)
    start_num_input.save_inputs(2)
    end_num_input.save_inputs(3)
    price.save_inputs(4)
    title.save_inputs(5)
    description.save_inputs(6)
    file_format.save_inputs(7)
    external_link.save_inputs(8)
    #metamask_pwd.save_inputs(10)
   
###Logging###
def log(message, force = False):
    if debug or force:
        print(message)

def i(val):
    val = val + 1
    return val

def gen_random_cdc():
    cdc = random.choices(string.ascii_lowercase, k=26)
    cdc[-6:-4] = map(str.upper, cdc[-6:-4])
    cdc[1] = 'j'
    cdc[2] = cdc[0] = 'd'
    cdc[3] = "_"
    return "".join(cdc).encode()

def is_binary_patched(executable_path):
    with open(executable_path, "rb") as fh:
        for line in iter(lambda: fh.readline(), b""):
            if (b"cdc_" in line) or force_patch :
                return False
        else:
            return True

def patch_exe(executable_path):

    linect = 0
    replacement = gen_random_cdc()
    with open(executable_path, "r+b") as fh:
        for line in iter(lambda: fh.readline(), b""):
            if b"cdc_" in line or (b"djd_" in line and force_patch):
                fh.seek(-len(line), 1)
                newline = re.sub(b"cdc_.{22}", replacement, line)
                fh.write(newline)
                linect += 1
        return linect

def sendKeys(field, value):
    for element in value:
        field.send_keys(element)

# _____MAIN_CODE_____
def main_program_loop():
    ###START###
    project_path = main_directory
    file_path = upload_path
    collection_link = collection_link_input.input_field.get()
    start_num = int(start_num_input.input_field.get())
    end_num = int(end_num_input.input_field.get())
    loop_price = float(price.input_field.get())
    loop_title = title.input_field.get()
    loop_file_format = file_format.input_field.get()
    loop_external_link = str(external_link.input_field.get())
    loop_description = description.input_field.get()
    loop_pwd = metamask_pwd.input_field.get()
    loop_delayBuffer = delayBuffer.input_field.get()
    loop_delayBuffer = 0 if loop_delayBuffer == '' else int(loop_delayBuffer)

    if not is_binary_patched(project_path + "/chromedriver"):
        patch_exe(project_path + "/chromedriver")

    open_chrome_profile()

    ##chromeoptions
    opt = Options()
    opt.add_experimental_option("debuggerAddress", "localhost:9515")
    opt.add_argument("screenshot")
    opt.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        executable_path=project_path + "/chromedriver",
        options=opt,
    )
    wait = WebDriverWait(driver, 60)

    driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])

    driver.delete_all_cookies()

    ###wait for methods
    def wait_css_selector(code):
        wait.until(
            ExpectedConditions.presence_of_element_located((By.CSS_SELECTOR, code))
        )
        
    def wait_css_selectorTest(code):
        wait.until(
            ExpectedConditions.elementToBeClickable((By.CSS_SELECTOR, code))
        )    

    def wait_xpath(code):
        wait.until(ExpectedConditions.presence_of_element_located((By.XPATH, code)))

    def wait_element(locator, value, failSoft=False):
        wait.until(ExpectedConditions.presence_of_element_located((locator, value)))

    def has_element(locator, value):
        try:
            driver.find_element(locator, value)
            return True
        except:
            return False

    def doMetaMaskLogin():
        if len(loop_pwd) > 3:
            log("Doing MetaMask Login")
            driver.get("chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/popup.html")
            time.sleep(2 + loop_delayBuffer)
            if not has_element(By.ID, "password"):
                if has_element(By.XPATH, "//div[@class=\"selected-account\"]"):
                    return
                else:
                    log("Doing MetaMask Login")
            else:
                wait_element(By.ID, "password")
                driver.find_element(By.ID, "password").send_keys(loop_pwd)
                wait_element(By.CSS_SELECTOR, "button[role='button']")
                driver.find_element(By.CSS_SELECTOR, "button[role='button']").click()

    def signIn():
        main_page = driver.current_window_handle
        for handle in driver.window_handles:
                if handle != main_page:
                    login_page = handle
        # change the control to signin page
        driver.switch_to.window(login_page)
        wait_css_selector("button[data-testid='request-signature__sign']")
        driver.find_element_by_css_selector("button[data-testid='request-signature__sign']").click()
        time.sleep(1 + loop_delayBuffer)
        # change control to main page
        driver.switch_to.window(main_page)
        time.sleep(1 + loop_delayBuffer)

    def doLogin():
        driver.delete_all_cookies()
        doMetaMaskLogin()
        time.sleep(2 + loop_delayBuffer)
        driver.get("https://opensea.io/login")
        time.sleep(2 + loop_delayBuffer)
        driver.find_element(By.XPATH, "//*[text()='MetaMask']/ancestor::button").click()
        driver.get(collection_link)
        try:
            driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
            driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a').click()
            time.sleep(5 + loop_delayBuffer)
            if len(driver.window_handles) > 1:
                log("MetaMask Sign - Popup appeared")
                signIn()
            return True
        except NoSuchElementException: 
            log("Unable to Login!!!")
            errorMessage['text'] = "Unable to Login!!!"
            return False

    def gotoCollection():
        driver.get(collection_link + "&__cf_chl_jschl_tk__=M4KGAW.65xMRW0feHHFeAQ9cYhwhO_YY9b_2H.7Agcc-1643016865-0-gaNycGzNCBE")
        time.sleep(5 + loop_delayBuffer)
        driver.delete_all_cookies()
            
    def gotoHome():
        driver.get("https://opensea.io/?__cf_chl_jschl_tk__=M4KGAW.65xMRW0feHHFeAQ9cYhwhO_YY9b_2H.7Agcc-1643016865-0-gaNycGzNCBE")
        time.sleep(5 + loop_delayBuffer)
        driver.delete_all_cookies()

    gotoHome()
    gotoCollection()

    while end_num >= start_num:  

        try:

            try:
                driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
                wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
                driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a').click()
                time.sleep(5 + loop_delayBuffer)
            except NoSuchElementException: 
                log("Not logged in - logging in now ")
                if not doLogin():
                    break
            
            log("Start creating NFT " +  loop_title + str(start_num))

            log("Adding Image " +  loop_title + str(start_num))
            wait_xpath('//*[@id="media"]')
            imageUpload = driver.find_element(By.XPATH, '//*[@id="media"]')
            imagePath = os.path.abspath(file_path + "/" + str(start_num) + "." + loop_file_format) 
            imageUpload.send_keys(imagePath)
            time.sleep(2 + loop_delayBuffer)

            log("Adding Name " +  loop_title + str(start_num))
            driver.find_element(By.XPATH, '//*[@id="name"]').send_keys(loop_title + str(start_num))  
            time.sleep(1 + loop_delayBuffer)

            log("Adding Link " +  loop_title + str(start_num))
            ext_link = driver.find_element(By.XPATH, '//*[@id="external_link"]')
            sendKeys(ext_link, loop_external_link)
            #driver.execute_script("arguments[0].value = '" + loop_external_link + "'", ext_link)
            time.sleep(1 + loop_delayBuffer)

            log("Adding Description " +  loop_title + str(start_num))
            desc = driver.find_element(By.XPATH, '//*[@id="description"]')
            #sendKeys(desc, loop_description)
            desc.send_keys(loop_description)
            #driver.execute_script("arguments[0].value = '" + loop_description + "'", desc)
            time.sleep(1 + loop_delayBuffer)

            if is_polygon.get():
                print("Switching to polygon " +  loop_title + str(start_num))
                driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div[7]/div/div[2]').click()
                polygon_button_location = '//span[normalize-space() = "Mumbai"]'
                wait.until(ExpectedConditions.presence_of_element_located((By.XPATH, polygon_button_location)))
                driver.find_element(By.XPATH, polygon_button_location).click()
                time.sleep(1 + loop_delayBuffer)

            log("Clicking Button " +  loop_title + str(start_num))
            create = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
            time.sleep(1 + loop_delayBuffer)
            driver.execute_script("arguments[0].click();", create)
            time.sleep(1 + loop_delayBuffer)

            log("Closing Popup " +  loop_title + str(start_num))
            wait_css_selector("i[aria-label='Close']")
            driver.find_element_by_css_selector("i[aria-label='Close']").click()
            time.sleep(2 + loop_delayBuffer)
            log('NFT minting completed!')

            if not skip_listing.get():
                log("NFT listing started " +  loop_title + str(start_num))
                main_page = driver.current_window_handle

                log("Clicking Sell Button " +  loop_title + str(start_num))
                wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
                driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a').click()
                time.sleep(1 + loop_delayBuffer)

                log("Adding Amount " +  loop_title + str(start_num))
                wait_css_selector("input[placeholder='Amount']")
                driver.find_element_by_css_selector("input[placeholder='Amount']").send_keys(str(loop_price))
                time.sleep(loop_delayBuffer) 

                # wait_xpath('//*[@id="duration"]')
                # driver.find_element(By.XPATH, '//*[@id="duration"]').click()

                # wait_xpath('//div[@role="dialog"]/div[2]/div[2]/div/div[2]/input[1]')
                # driver.find_element(By.XPATH, '//div[@role="dialog"]/div[2]/div[2]/div/div[2]/input[1]').send_keys(Keys.ARROW_UP)

                log("Clicking Complete Button " +  loop_title + str(start_num))
                wait_css_selector("button[type='submit']")
                driver.find_element_by_css_selector("button[type='submit']").click()
                time.sleep(5 + loop_delayBuffer)
                
                log("Clicking Sign Button " +  loop_title + str(start_num))
                wait_css_selector("button[class='Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 bhqEJb fzwDgL']")
                driver.find_element_by_css_selector("button[class='Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 bhqEJb fzwDgL']").click()
                time.sleep(2 + loop_delayBuffer)
                
                log("Switching to MetaMask Sign Popup " +  loop_title + str(start_num))
                for handle in driver.window_handles:
                    if handle != main_page:
                        login_page = handle
                # change the control to signin page
                driver.switch_to.window(login_page)

                log("Clicking Sign Button " +  loop_title + str(start_num))
                wait_css_selector("button[data-testid='request-signature__sign']")
                driver.find_element_by_css_selector("button[data-testid='request-signature__sign']").click()
                time.sleep(2 + loop_delayBuffer)
                
                log("Switching Back TO OpenSea " +  loop_title + str(start_num))
                # change control to main page
                driver.switch_to.window(main_page)
                time.sleep(1 + loop_delayBuffer)
                log('NFT listing completed! ' +  loop_title + str(start_num))

                wait_xpath("//*[text()='close']/ancestor::button")
                driver.find_element(By.XPATH, "//*[text()='close']/ancestor::button").click()
                time.sleep(2 + loop_delayBuffer)

            wait_xpath("//section[@class='item--header']//a")
            driver.find_element(By.XPATH, "//section[@class='item--header']//a").click()
            time.sleep(1 + loop_delayBuffer)

            log('NFT creation completed for NFT:' +  loop_title + str(start_num))
            start_num = start_num + 1
            start_num_input.insert_text(start_num)
            save()
            time.sleep(2 + loop_delayBuffer)

        except Exception:
            gotoHome()
            gotoCollection()
            pass

        
###input objects###

#row counter
r = 1

bufferLabel = Label(root)
bufferLabel.grid(row=(r := r+1), column=0,padx=5, pady=5)

upload_path_input = InputField("NFTs Upload folder:", (r := r+1), 0, 0)
upload_path = upload_path_input.input_field.get()

upload_folder_input_button = ttk.Button(root, width=2, text="...", command=upload_folder_input)
upload_folder_input_button.grid(row=(r), column=2, padx=5, pady=5)

collection_link_input = InputField("OpenSea Collection Link:", (r := r+1), 0, 1)

start_num_input = InputField("Start Number:", (r := r+1), 0, 2)
end_num_input = InputField("End Number:", (r := r+1), 0, 3)
price = InputField("Price:", (r := r+1), 0, 4)
title = InputField("Title:", (r := r+1), 0, 5)
description = InputField("Description:", (r := r+1), 0, 6)
file_format = InputField("NFT Image Format:", (r := r+1), 0, 7)
external_link = InputField("External link:", (r := r+1), 0, 8)
metamask_pwd = InputField("Metamask Pwd:", (r := r+1), 0, 10, showVal="*")
delayBuffer = InputField("Cloudflare buffer delay:", (r := r+1), 0, 11)

#####BUTTON ZONE#######
style = ttk.Style()
style.theme_use('alt')
style.configure('TLabel', background = 'white', foreground = 'black', width = 20, borderwidth=1, focusthickness=3, focuscolor='none')
style.configure('TButton', background = '#0074CC', foreground = 'white', width = 20, borderwidth=1, focusthickness=3, focuscolor='none')
style.configure('TCheckbutton', foreground='blue')
style.map('TButton', background=[('active','lightgreen')])

isPoligonLAbel = Label(root, text="Use Polygon Blockchain")
isPoligonLAbel.grid(row=(r := r+1), column=0)
isPolygon = tkinter.Checkbutton(root, var=is_polygon)
isPolygon.grid(row=r, column=1)

isSkipLAbel = Label(root, text="Skip Listing")
isSkipLAbel.grid(row=(r := r+1), column=0)
isSkip = tkinter.Checkbutton(root, var=skip_listing)
isSkip.grid(row=r, column=1)

isHeadLess = Label(root, text="Run headless")
isHeadLess.grid(row=(r := r+1), column=0)
isHeadLess = tkinter.Checkbutton(root, var=headless)
isHeadLess.grid(row=r, column=1)

button_save = ttk.Button(root, width=20, text="Save Form", command=save) 
button_save.grid(row=(r := r+1), column=0, padx=5, pady=5)

open_browser = ttk.Button(root, width=20,  text="Open Chrome Browser", command=open_chrome_profile)
open_browser.grid(row=r, column=1, padx=5, pady=5)

button_start = ttk.Button(root, width=20, text="Start", command=main_program_loop)
button_start.grid(row=r, column=2, padx=5, pady=5)

errorMessage = Label(root, text="No Error.")
errorMessage.grid(row=(r := r+1), column=0, columnspan=4)
errorMessage['text'] = ""

#####BUTTON ZONE END#######
root.mainloop()
