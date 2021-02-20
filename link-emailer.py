import requests
from bs4 import BeautifulSoup
import random
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

def make_GUI():
    root = tk.Tk()
    root.title("Digital Paper Scraper")

    canvas = tk.Canvas(root, width=600, height=300)
    canvas.grid(columnspan=11, rowspan=16)

    #picture
    img = Image.open('cat.png')
    img = img.resize((250, 250), Image.ANTIALIAS) #must be here.  Can't be after the ImageTk.PhotoImage line
    img = ImageTk.PhotoImage(img) #PIL object
    img_label = tk.Label(image=img)
    img_label.image = img
    img_label.grid(columnspan = 11, column = 0, rowspan = 5, row = 0)

    #instructions
    instructions = tk.Label(root, text="Instructions, Instructions, Instructions, Instructions, Instructions")
    instructions.grid(columnspan = 11, column = 0, row=6)

    #checkbox options
    CheckVar1 = IntVar()
    CheckVar2 = IntVar()
    amazon = Checkbutton(root, text = "Amazon", variable = CheckVar1, onvalue = 1, offvalue = 0)
    kijiji = Checkbutton(root, text = "Kijiji", variable = CheckVar2, onvalue = 1, offvalue = 0)
    amazon.grid(column = 4, row = 7)
    kijiji.grid(column = 6, row = 7)

    #clear placeholder txt in entry boxes when clicked on
    def clear_entry(event, entry):
        entry.delete(0, END)
        entry.configure(fg='black')
        entry.unbind('<Button-1>', click_event)

    #search terms field
    searchVar = StringVar()
    search_terms = Entry(root, bd = 5, textvariable = searchVar, fg='gray')
    search_terms.grid(columnspan = 9, column = 1, row = 8)
    search_terms.insert(0, 'Search Terms')
    search_terms.bind("<Button-1>", lambda event: clear_entry(event, search_terms))

    #email field
    emailVar = StringVar()
    email = Entry(root, textvariable = emailVar, bd = 5, fg='gray')
    email.grid(columnspan = 9, column = 1, row = 9)
    email.insert(0, "Email")
    email.bind("<Button-1>", lambda event: clear_entry(event, email))

    #notification preferences
    not_pref = tk.Label(root, text="How often do you want to be notified? Every:")
    not_pref.grid(columnspan = 11, column = 0, row=10)

    #minutes field
    minVar = StringVar()
    minutes = Entry(root, textvariable = minVar, bd = 5, fg='gray')
    minutes.grid(columnspan = 3, column = 1, row = 11)
    minutes.insert(0, "Minutes")
    minutes.bind("<Button-1>", lambda event: clear_entry(event, minutes))

    #hours field
    hourVar = StringVar()
    hours = Entry(root, textvariable = hourVar, bd = 5, fg='gray')
    hours.grid(columnspan = 3, column = 4, row = 11)
    hours.insert(0, "Hours")
    hours.bind("<Button-1>", lambda event: clear_entry(event, hours))

    #days field
    daysVar = StringVar()
    days = Entry(root, textvariable = daysVar, bd = 5, fg='gray')
    days.grid(columnspan = 3, column = 7, row = 11)
    days.insert(0, "Days")
    days.bind("<Button-1>", lambda event: clear_entry(event, days))

    def button_command():
        #while True:
        search = search_terms.get()
        to_email = email.get()
        try:
            mins = int(minutes.get())
        except ValueError:
            mins = 0
        try:
            hrs = int(hours.get())
        except ValueError:
            hrs = 0
        try:
            day = int(days.get())
        except ValueError:
            day = 0             
        
        auto_email(search, to_email, scrape_amazon(search), scrape_kijiji(search))
        
        if mins == 0 and hrs == 0 and day == 0:
            return
        else:
            wait_minutes = mins + (hrs * 60) + (day * 24 * 60)
            print(f'Repeating in {mins} minutes, {hrs} hours, and {day} days...')
            #time.sleep(wait_minutes * 60) #doesn't work with while loop within the infinite loop of GUI mainloop()
            #calls the function again automatically (time in ms)
            root.after(wait_minutes * 60000, button_command)

    #submit button. Note that command must be a lambda function to avoid execution at program start
    #go = tk.Button(root, text ="GET GOING", command = lambda: auto_email(search, scrape_amazon(), scrape_kijiji()))
    go = tk.Button(root, text ='GET GOING', command = button_command)
    go.configure(highlightbackground="blue")
    go.grid(columnspan = 5, column = 3, row = 12, sticky='nsew')

    # call the mainloop, which creates the GUI.  Everything must be above this.
    root.mainloop()

def scrape_kijiji(search):
    print('Checking Kijiji...')
    ind_terms = search.split()
    base_URL = 'https://www.kijiji.ca/b-gta-greater-toronto-area/'

    URL_add = ind_terms[0]
    if len(ind_terms) > 1:
        for i in range(1, len(ind_terms)):
            URL_add += '-' + ind_terms[i] 
    URL = base_URL + URL_add + '/k0l1700272?rb=true&dc=true'

    headers = {
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
    }

    #from https://stackoverflow.com/questions/41366099/getting-blocked-when-scraping-amazon-even-with-headers-proxies-delay: 
    proxies_list = ["128.199.109.241:8080","113.53.230.195:3128","125.141.200.53:80","125.141.200.14:80","128.199.200.112:138","149.56.123.99:3128","128.199.200.112:80","125.141.200.39:80","134.213.29.202:4444"]
    proxies = {'https//': random.choice(proxies_list)}

    page = requests.get(URL, headers=headers, proxies=proxies)
    #check for HTTP status code exceptions
    try:
        page.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    soup = BeautifulSoup(page.content, "lxml")

    items = soup.find_all('div', class_='info')
    k_options = []
    for item in items:
        title = item.find('div', class_='title').get_text().strip()
        link = 'kijiji.ca' + item.find('a', class_='title').get('href')
        try:
            price = item.find('div', class_='price').get_text().strip()
            price = float(price[1:])
        except: 
            price = 'no price listed'
        try:
            posted_date = item.find('span', class_='date-posted').get_text().strip()
        except:
            posted_date = 'no date listed'
        iteminfo = {}
        iteminfo['title'] = title
        iteminfo['link'] = link
        if isinstance(price, float):
            iteminfo['price'] = int(price)
        else:
            continue
        iteminfo['posted_date'] = posted_date
        k_options.append(iteminfo)
    
    k_options = sorted(k_options, key = lambda i: i['price'])
    for option in k_options:
        option['price'] = f"${option['price']}"
    return k_options

def scrape_amazon(search):
    print('Checking Amazon...')
    #search = '1440p Monitor'
    ind_terms = search.split()
    base_URL = 'https://www.amazon.ca/s?k='

    URL = base_URL + ind_terms[0]
    if len(ind_terms) > 1:
        for i in range(1, len(ind_terms)):
            URL = URL + '+' + ind_terms[i]
    
    #googled these, as per DevEd videos - but it didn't work. 
    #headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}

    # simulate the headers that amazon uses when a request is made FROM THE BROWSER (as opposed to from code) by following this guide: https://stackoverflow.com/questions/41366099/getting-blocked-when-scraping-amazon-even-with-headers-proxies-delay
    #and this link: https://curl.trillworks.com/
    headers = {
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
    }

    #from https://stackoverflow.com/questions/41366099/getting-blocked-when-scraping-amazon-even-with-headers-proxies-delay: 
    proxies_list = ["128.199.109.241:8080","113.53.230.195:3128","125.141.200.53:80","125.141.200.14:80","128.199.200.112:138","149.56.123.99:3128","128.199.200.112:80","125.141.200.39:80","134.213.29.202:4444"]
    proxies = {'https//': random.choice(proxies_list)}

    page = requests.get(URL, headers=headers, proxies=proxies)
    #check for HTTP status code exceptions
    try:
        page.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    soup = BeautifulSoup(page.content, "lxml") #could also use bulit-in python parser "html.parser", but lxml is faster

    #print(soup.prettify())
    items = soup.find_all('div', class_='s-expand-height s-include-content-margin s-border-bottom s-latency-cf-section')
    a_options = []
    for item in items:
        title = item.find('span', class_='a-size-base-plus a-color-base a-text-normal').get_text().strip()
        link = 'amazon.ca' + item.find('a', class_='a-link-normal a-text-normal').get('href')
        try:
            price = item.find('span', class_='a-price-whole').get_text().strip()
            price = float(price)
        except: 
            price = 99999
        try:
            rating = item.find('span', class_='a-icon-alt').get_text().strip()
        except:
            rating = 'no ratings'
        try:
            reviews = item.find('span', class_='a-size-base')
        except:
            reviews = 'no reviews'
        iteminfo = {}
        iteminfo['title'] = title
        iteminfo['link'] = link
        iteminfo['price'] = price
        iteminfo['rating'] = rating
        iteminfo['reviews'] = reviews
        a_options.append(iteminfo)
    
    a_options = sorted(a_options, key = lambda i: i['price'])
    for option in a_options:
        option['price'] = f"${option['price']}"
    return a_options

"""  
    #write all results to a CSV file
    import csv
    with open('options.csv', 'w', newline='') as f:
        header = ['title', 'link', 'price'] 
        writer = csv.DictWriter(f, fieldnames = header)
        writer.writeheader() 
        for option in options:
            writer.writerow(option)
"""

    # converted_price = int(price[5:8].replace(',',''))


def auto_email(search, email, a_options, k_options):
    #email credentials added to PATH via running nano .bash_profile in terminal and adding them to profile
    from_email = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')
    to_email = email #'webdevinci.code@gmail.com'
    port = 587
    server = 'smtp.gmail.com'
    
    message = MIMEMultipart("alternative")
    message["From"] = from_email
    message["To"] = to_email

    subject = "Here's some options for the {} you were interested in..."
    subject = subject.format(search)
    message["Subject"] = subject

    # Create the plain-text and HTML version of your message    
    text = """\
    ---Plain Text---
    Kijiji:
    {}
    Amazon:
    {}
    """

    html = """\
    <html>
        <body>
            {}<br>
            {}
        </body>
    </html>
    """
    if len(a_options) < 1:
        html = "<p>None found</p>"
    
    a_rows=''
    for option in a_options:
        data = ''
        for value in option.values():
            data = data + "<td>"+str(value)+"</td>"
        a_rows = a_rows + "<tr>"+data+"</tr>" 

    k_rows=''
    for option in k_options:
        data = ''
        for value in option.values():
            data = data +"<td>"+str(value)+"</td>"
        k_rows = k_rows + "<tr>"+data+"</tr>"
        
    if len(a_options) < 1:
        amazon_html = """ <h2>Nothing Found on Amazon</h2> """
    else:
        amazon_html = """
            <h2>Check Out These Amazon Links:</h2>
                <table border = 1px solid black>
                    <th>Title</th>
                    <th>Link</th>
                    <th>Price</th>
                    <th>Rating</th>
                    <th>Reviews</th>
                    <tbody>
                        {}
                    </tbody>
                </table>
        """
        amazon_html = amazon_html.format(a_rows)

    if len(k_options) < 1:
        kij_html = """ <h2>Nothing Found on Kijiji</h2> """
    else:
        kij_html = """
            <h2>Check Out These Kijiji Links:</h2>
                <table border = 1px solid black>
                    <th>Title</th>
                    <th>Link</th>
                    <th>Price</th>
                    <th>Date Posted</th>
                    <tbody>
                        {}
                    </tbody>
                </table>
        """
        kij_html = kij_html.format(k_rows)

    html = html.format(kij_html, amazon_html)
    text = text.format(kij_html, amazon_html)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)
    print('Connecting to email server...')
    try:
        smtpObj = smtplib.SMTP(server, port)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(from_email, password)
        print("Sending Email...")
        smtpObj.sendmail(from_email, to_email, message.as_string()) #must send msg as.string() when using HTML and plaintext options
        print('Email Sent!')
    except Exception as e:
        print(e)
    finally:
        smtpObj.quit()

if __name__ == '__main__':
    
    #search = 'Dog Collar'
    make_GUI()
    #auto_email(webscrape())
    
