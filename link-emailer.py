# A desktop app that allows kijiji and amazon webscraping and automatic email notifications

# import requests to grab website HTML
import requests
# import BS4 for webscraping
from bs4 import BeautifulSoup
# import random to randomly choose a proxy for the URL request (to help fool anti-scrapers)
import random
import time
# import os to access os variables like email and password
import os
# import smtplib to enable connecting to email server
import smtplib
# mime lets you send plain text and html emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# tkinter is the python GUI
import tkinter as tk
# import using * wildcard so you don't need to use any 'tk' prefixes
from tkinter import *
# PIL (or pillow) allows you to use images in tkinter
from PIL import Image, ImageTk

def main():
    #global variable used in countdown function later
    t = 0 

    #clear placeholder txt in entry boxes when clicked on
    def clear_entry(event, entry):
        entry.delete(0, END)
        entry.configure(fg='black')
    
    # countdown function to get live GUI countdown
    def countdown():
        global t
        days = (t // 86400)
        hours = (t - days * 86400) // 3600
        minutes = (t - days * 86400 - hours * 3600) // 60
        secs = t % 60
        if t >= 0:
            #ds-digital font is a downloaded font on my computer
            timer.configure(bg = 'black', fg = 'red', font = ('ds-digital', '26', 'bold'))
            timer['text'] = '{:02d}:{:02d}:{:02d}:{:02d}'.format(days, hours, minutes, secs)
            root.update()
            t -= 1
            # call countdown every 1000ms and update timer
            timer.after(1000, countdown)
    
    # executes when the GUI button is clicked
    def button_command():
        #reset any past statuses to blank
        amazon_status['text'] = ''
        kij_status['text'] = ''
        email_status1['text'] = ''
        email_status2['text'] = ''
        email_status3['text'] = ''
        repeat_msg['text'] = ''
        timer.configure(bg = 'white')
        timer['text'] = ''
        # update the root window to display these changes
        root.update()

        print(f"rare = {rareCheck.get()}, amazon = {amazoncheck.get()}, kij = {kijijicheck.get()}, low = {low_price_box.get()}, high = {high_price_box.get()}, dealer = {dealercheck.get()}")
        # grab user input from text boxes on GUI
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
        #run functions
        if amazoncheck.get() == False and kijijicheck.get() == False:
            return
        elif amazoncheck.get() == True and kijijicheck.get() == False:
            a_results = scrape_amazon(search)
            k_results = 'Not Selected'
        elif kijijicheck.get() == True and amazoncheck.get() == False:
            k_results = scrape_kijiji(search)
            a_results = 'Not Selected'
        else:
            a_results = scrape_amazon(search)
            k_results = scrape_kijiji(search)
        # check email conditions
        if rareCheck.get() == True:
            if (a_results != 'Not Selected' and len(a_results) > 0) or (k_results != 'Not Selected' and len(k_results) > 0):
                auto_email(search, to_email, a_results, k_results)
            else:
                print('No Results!')
                email_status1.configure(text = "No Results!")
                pass
        else:
            auto_email(search, to_email, a_results, k_results)

        #set timeline to repeat this function
        if mins == 0 and hrs == 0 and day == 0:
            return
        else:
            #countdown(mins=mins, hrs=hrs, day=day)
            wait_minutes = mins + (hrs * 60) + (day * 24 * 60)
            print(f'Repeating in {mins} minutes, {hrs} hours, and {day} days...')
            repeat_msg['text'] = f'Repeating process in:\n {day} day(s),\n {hrs} hour(s), and \n {mins} min(s)'
            root.update()
            global t
            t = (mins * 60) + (hrs * 60 * 60) + (day * 24 * 60 * 60)
            countdown()
            #time.sleep(wait_minutes * 60) #doesn't work with while loop within the infinite loop of GUI mainloop()
            #calls the function again automatically (time in ms)
            root.after(wait_minutes * 60000, button_command)

    root = tk.Tk()
    root.title("Digital Paper Scraper")

    #canvas = tk.Canvas(root, width=600, height=500)

    #picture
    img = Image.open('cat.png')
    img = img.resize((250, 250), Image.ANTIALIAS) #must be here.  Can't be after the ImageTk.PhotoImage line
    img = ImageTk.PhotoImage(img) #PIL object
    img_label = tk.Label(image=img)
    img_label.image = img

    #instructions
    instructions = tk.Label(root, text="YOU LOOKING TO SPEND SOME CASH MONEY??? \n Let the online-shopping cat guide you.  Choose your options below:")

    #checkbox options
    amazoncheck = IntVar()
    kijijicheck = IntVar()
    amazon = Checkbutton(root, text = "Amazon", variable = amazoncheck, onvalue = True, offvalue = False, fg = 'black')
    kijiji = Checkbutton(root, text = "Kijiji", variable = kijijicheck, onvalue = True, offvalue = False, fg = 'black')

    #search terms field
    searchVar = StringVar()
    search_terms = Entry(root, bd = 5, textvariable = searchVar, fg='gray')
    search_terms.insert(0, 'Search Terms')
    search_terms.bind("<Button-1>", lambda event: clear_entry(event, search_terms))

    #kijiji filter dealer option
    dealercheck = IntVar()
    dealer = Checkbutton(root, text = 'Filter Out Kijiji Distributors', variable = dealercheck, onvalue = True, offvalue = False)

    # price filter options
    price_rng_label = tk.Label(root, text = 'Only show me items with prices between:')

    low_price_box = Entry(root, bd = 5, fg = 'gray', width = 8)
    low_price_box.insert(0, "Min")
    low_price_box.bind("<Button-1>", lambda event: clear_entry(event, low_price_box))

    high_price_box = Entry(root, bd = 5, fg = 'gray', width = 8)
    high_price_box.insert(0, "Max")
    high_price_box.bind("<Button-1>", lambda event: clear_entry(event, high_price_box))

    # filter out kijiji dealers
    rareCheck = IntVar()
    rare = Checkbutton(root, text = 'Only Email Me If There Are Results', variable = rareCheck) 

    #email field
    emailVar = StringVar()
    email = Entry(root, textvariable = emailVar, bd = 5, fg='gray')
    email.insert(0, "Email")
    email.bind("<Button-1>", lambda event: clear_entry(event, email))

    #notification preferences
    not_pref = tk.Label(root, text="Notify me every:")

    #minutes field
    minVar = StringVar()
    minutes = Entry(root, textvariable = minVar, bd = 5, fg='gray', width = 8)
    minutes.insert(0, "Minutes")
    minutes.bind("<Button-1>", lambda event: clear_entry(event, minutes))

    #hours field
    hourVar = StringVar()
    hours = Entry(root, textvariable = hourVar, bd = 5, fg='gray', width = 8)
    hours.insert(0, "Hours")
    hours.bind("<Button-1>", lambda event: clear_entry(event, hours))

    #days field
    daysVar = StringVar()
    days = Entry(root, textvariable = daysVar, bd = 5, fg='gray', width = 8)
    days.insert(0, "Days")
    days.bind("<Button-1>", lambda event: clear_entry(event, days))

    #function status logs
    amazon_status = tk.Label(root, text = '', width = 35)
    kij_status = tk.Label(root, text='')
    email_status1 = tk.Label(root, text = '')
    email_status2 = tk.Label(root, text = '')
    email_status3 = tk.Label(root, textv = '')
    repeat_msg = tk.Label(root, text='')
    timer = tk.Label(root, text = '')

    #submit button. Note that command must be a lambda function to avoid execution at program start
    go = tk.Button(root, text ='GET GOING', command = button_command)
    go.configure(highlightbackground="blue", fg = "white", relief = RAISED)

    #canvas.grid(columnspan=6, rowspan=20)
    img_label.grid(column = 2, columnspan = 2, rowspan = 11, row = 0)
    instructions.grid(column = 0, columnspan = 6, rowspan = 2, row=11, padx = 20)
    amazon.grid(column = 2, row = 13)
    kijiji.grid(column = 3, row = 13)
    search_terms.grid(column = 0, columnspan = 6, row = 14, sticky = NSEW, padx = 20)
    dealer.grid(column = 2, columnspan = 2, row = 15, sticky = W)
    price_rng_label.grid(column = 0, columnspan = 2, row = 17, padx = 20, sticky = E)
    low_price_box.grid(column = 2, row = 17)
    high_price_box.grid(column = 3, row = 17)
    rare.grid(column = 2, columnspan = 2, row = 16, sticky = W)
    email.grid(column = 0, columnspan = 6, row = 19, sticky = NSEW, padx = 20)
    not_pref.grid(column = 0, columnspan = 2, row=18, padx = 20, sticky = E)
    minutes.grid(column = 2, row = 18)
    hours.grid(column = 3, row = 18)
    days.grid(column = 4, row = 18, sticky = W, padx = 18)
    amazon_status.grid(column = 4, columnspan = 2, row = 1)
    kij_status.grid(column = 4, columnspan = 2, row = 2)
    email_status1.grid(column = 4, columnspan = 2, row = 3)
    email_status2.grid(column = 4, columnspan = 2, row = 4)
    email_status3.grid(column = 4, columnspan = 2, row = 5)
    repeat_msg.grid(column = 4, columnspan = 2, row = 6, rowspan = 4, pady = 10)
    timer.grid(column = 4, columnspan = 2, row = 10, pady = 10)
    go.grid(column = 2, columnspan = 2, row = 20, sticky='nsew', pady = 20)

    def scrape_kijiji(search):
        print('Checking Kijiji...')
        kij_status.configure(text = "Checking Kijiji...")
        root.update()
        # split the inputted search terms into separate words and add to URL
        ind_terms = search.split()
        base_URL = 'https://www.kijiji.ca/b-gta-greater-toronto-area/'

        URL_add = ind_terms[0]
        if len(ind_terms) > 1:
            for i in range(1, len(ind_terms)):
                URL_add += '-' + ind_terms[i] 
        URL = base_URL + URL_add + '/k0l1700272?rb=true&dc=true'

        # these come from the dev tab in chrome, network tab, copying a request as cURL, and translating to python
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

        # access URL
        page = requests.get(URL, headers=headers, proxies=proxies)
        #check for HTTP status code exceptions
        try:
            page.raise_for_status()
        except Exception as exc:
            print('There was a problem: %s' % (exc))

        # get HTML of URL
        soup = BeautifulSoup(page.content, "lxml")
        
        # find all divs with class info in the HTML
        items = soup.find_all('div', class_='info')
        k_options = []
        #print(dealercheck.get())
        # check if user selected to filter out kijiji dealers
        if dealercheck.get() == True:
            for item in items:
                #filter out any kijiji ads that have a dealer logo image
                if soup.find('div', class_="dealer-logo-image"):
                    continue
                else:
                    title = item.find('div', class_='title').get_text().strip()
                    link = 'kijiji.ca' + item.find('a', class_='title').get('href')
                    try:
                        price = item.find('div', class_='price').get_text().strip().replace(',','')
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
                    #print(f'price is {price}, high is {high_price_box.get()}, low is {low_price_box.get()}')
                    # all these lines check the values of the input boxes on the GUI for price filtering
                    if high_price_box.get() != 'Max' and high_price_box.get() != '' and low_price_box.get() != 'Min' and low_price_box.get() != '':
                        if float(high_price_box.get()) >= price and float(low_price_box.get()) <= price:
                            k_options.append(iteminfo)
                    elif high_price_box.get() != 'Max' and low_price_box.get() == 'Min':
                        if float(high_price_box.get()) >= price:
                            k_options.append(iteminfo)
                    elif high_price_box.get() == 'Max' and low_price_box.get() != 'Min':
                        if float(low_price_box.get()) <= price:
                            k_options.append(iteminfo)
                    elif high_price_box.get() == 'Max' and low_price_box.get() == 'Min':
                        k_options.append(iteminfo)
        # if we don't have to filter out kijiji dealers:            
        else:
            for item in items:
                title = item.find('div', class_='title').get_text().strip()
                link = 'kijiji.ca' + item.find('a', class_='title').get('href')
                try:
                    price = item.find('div', class_='price').get_text().strip().replace(',','')
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
                #print(f'price is {price}, high is {high_price_box.get()}, low is {low_price_box.get()}')
                if high_price_box.get() != 'Max' and low_price_box.get() != 'Min':
                    if float(high_price_box.get()) >= price and float(low_price_box.get()) <= price:
                        k_options.append(iteminfo)
                elif high_price_box.get() != 'Max' and low_price_box.get() == 'Min':
                    if float(high_price_box.get()) >= price:
                        k_options.append(iteminfo)
                elif high_price_box.get() == 'Max' and low_price_box.get() != 'Min':
                    if float(low_price_box.get()) <= price:
                        k_options.append(iteminfo)
                elif high_price_box.get() == 'Max' and low_price_box.get() == 'Min':
                    k_options.append(iteminfo)
        # sort by price.  Have to use a lambda function here, not sure why.
        k_options = sorted(k_options, key = lambda i: i['price'])
        for option in k_options:
            option['price'] = f"${option['price']}"
        return k_options

    def scrape_amazon(search):
        print('Checking Amazon...')
        amazon_status['text'] = ('Checking Amazon...')
        root.update()
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
                'authority': 'www.amazon.ca',
                'cache-control': 'max-age=0',
                'rtt': '50',
                'downlink': '10',
                'ect': '4g',
                'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'service-worker-navigation-preload': 'true',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-US,en;q=0.9',
                'cookie': 'session-id=136-5401344-1509546; ubid-acbca=131-9816716-5018158; x-acbca="ppQleUBEqdXZ7prk9clrIu@zqZVupYMefDBePGfi8?V6DFiYqDU08B@ctP@dlnOM"; at-acbca=Atza|IwEBIDj34OuBn6fqCF90Mwi7Bz1k1fK-I8nR9R3Th2QqWFLVDOVl2_1h06x7NphYRfJ1jRJWfQhldflLJcxNJ3u7VAvHpWmlOSDMOtcbI_QZMPA6CX26zMuKgnZt04RlOPIpgDshYXn2mwdjLb8f9-P58QlbeAkLtRRNNIJYYNY7pGctiJ3xmlijDpbBKZD7QPRhHbVhO6b6XK720wm1JeydEXxd; sess-at-acbca="fLZNru5ZVSIGlQZ/nh19jJlRotWBAYG7vjEFH+FI2d4="; sst-acbca=Sst1|PQHNJv9jH1eE_eN4H8pr1pJDCVJtT0pjE52qcpSyxs6giEa1BKgDYy0eTbwtIkEGp_xwIAKaHO7gA-TsjaFU48027hyG2IUy3NMMTc22cOYsaENIE6Teiv90eYJIfm53jitMr41EuYpCnZtfJ66HhwSm7AmabITEfiKB9xr9Ll2dOJk_sz-7C-h2Cv21fBdCE_JNRcj1QADhpPJJ7VLfRfodmLMb4bHdrIa2rlnSHDNL9OI2F_gUNK7EFdRA9LMhdPR0DlJQ_yl_QweyShRCbdy12wb8ElL4RH8G-hOutDF0XMs; lc-acbca=en_CA; session-id-time=2082787201l; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiN2EzYzJmIiwia2V5IjoiWi9BbnRpbG5FSFFoaGNJeTl1QWhnWmVFcitjeHdsTEZsL01acTlWK1RXV1pPS0ZVYVlPN2YxNkNGWFhUQmI1ZmFFWEQvT25jVkZqZ2pDTm9TODZxM2t3RXppTGM3UHhENGRSZCt4eENoT2l5bGl5ZjZ2UmlnY3poSjBaUWQ1Q1NRV3h0bERqZHpCaUo0VXp1dkZWb2JWblZVdjlQQ0VZNG5MRkFNZ2xwZXI4ck5RQ2ZtRktVWnRyWWRVZ3FsWkNWMmhkOTVsMWVVWlFXam9Jbkoxc295a3g5aXFyekZnQ0hnWjlsQm5PcllNN0x6bU5nZmt6cU51cCtVQXNLT2NPWG15UStpZFg1MWVOcDlXSjNVVGM1ekhsUE01SU56QUUvcnhIQWV2ejVxYzZ5d3NVbGpQOU5qd1J3c2pNMGhFMjR4YzJxWEU4N3lMNmE5UWNaMWNlQjdnPT0ifQ==; i18n-prefs=CAD; session-token="rIvMtbZvs7BdMCBYRlR0ImpMkf+ajeh0KKtwVj0YoxBLNiT2jXABlsVpwIaKLGlIU1qibzFkSfky9J6NszzOsaM8jS+AN2vE3X2dhKShFApfIg0IKeIBa0N3TxhMCWY6DbKTLSsLYh2y8ROHCpHtr+GflsRnstfthzbwmMMpSAvMLv89BpTaY00bNtqxfZx3vKPz63fllIlVpibKMHG8TA=="; csm-hit=tb:CBEQR9MZBX9P71V6X84K+s-CBEQR9MZBX9P71V6X84K|1614033908692&t:1614033908692&adb:adblk_yes',
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
                price = item.find('span', class_='a-price-whole').get_text().strip().replace(',','')
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
            #print(f'price is {price}, high is {high_price_box.get()}, low is {low_price_box.get()}')
            if high_price_box.get() != 'Max' and low_price_box.get() != 'Min':
                if float(high_price_box.get()) >= price and float(low_price_box.get()) <= price:
                    a_options.append(iteminfo)
            elif high_price_box.get() != 'Max' and low_price_box.get() == 'Min':
                if float(high_price_box.get()) >= price:
                    a_options.append(iteminfo)
            elif high_price_box.get() == 'Max' and low_price_box.get() != 'Min':
                if float(low_price_box.get()) <= price:
                    a_options.append(iteminfo)
            elif high_price_box.get() == 'Max' and low_price_box.get() == 'Min':
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

        # Create the plain-text and HTML version of message    
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
        # check if user asked for results from amazon or kijiji
        if a_options == 'Not Selected':
            amazon_html = ''
        elif len(a_options) < 1:
            amazon_html = """ <h2>Nothing Found on Amazon</h2> """
        else:
            a_rows=''
            for option in a_options:
                data = ''
                for value in option.values():
                    data = data + "<td>"+str(value)+"</td>"
                a_rows = a_rows + "<tr>"+data+"</tr>" 

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

        if k_options == 'Not Selected':
            kij_html = ''
        elif len(k_options) < 1:
            kij_html = """ <h2>Nothing Found on Kijiji</h2> """
        else:
            k_rows=''
            for option in k_options:
                data = ''
                for value in option.values():
                    data = data +"<td>"+str(value)+"</td>"
                k_rows = k_rows + "<tr>"+data+"</tr>"

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
        email_status1['text'] = 'Connecting to email server...'
        root.update()
        try:
            smtpObj = smtplib.SMTP(server, port)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(from_email, password)
            print("Sending Email...")
            email_status2['text'] = 'Sending Email...'
            root.update()
            smtpObj.sendmail(from_email, to_email, message.as_string()) #must send msg as.string() when using HTML and plaintext options
            print('Email Sent!')
            email_status3['text'] = 'Email Sent!'
            root.update()
        except Exception as e:
            print(e)
            email_status3['text'] = "Couldn't Send Email!"
            root.update()
        finally:
            smtpObj.quit()

    # call the mainloop, which creates the GUI.  Everything must be above this.
    root.mainloop()

if __name__ == '__main__':
    main()
    
    
