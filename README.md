# Digital Paper Scraper

#### Version 1.0.0

## A python desktop app with Tkinter GUI for automatically webscraping Kijiji and Amazon with user input criteria

### This was created as my final project for Harvard's CS50x online course - Intro to Computer Science

### Video Demo: https://www.youtube.com/watch?v=8X9YP-M9vxk&feature=youtu.be

### Motivation

When you're looking for a good deal, constantly checking Kijiji and Amazon for the item, filtering by criteria, and comparing results can be tedious. This desktop application helps automate the process.

### Necessary New Skills

To make this program, I had to learn:

1. python GUIs

   - what GUIs are and how they work (continuous loops, user input, widget organization, etc)
   - which GUIs are available in Python
   - how to integrate them into software (arrangement, function calls, etc)
   - displaying dynamic content
   - downloading custom fonts

2. webscraping

   - modules available (beautiful soup vs selenium)
   - how to download browser drivers
   - how to access typical headers from cURL requests
   - what proxies are and why to use them
   - what HTML parsers are and how/why to use them
   - how to trick anti-webscraping tools deployed by developers (particularly Amazon)
   - how to organize and iterate through HTML

3. automatic emailing

   - connecting to an email server
   - using environmental variables to keep sensitive info private
   - TTP vs SSL emails
   - plain text vs HTML emails
   - auto formatting HTML for dynamic content in python
   - using Gmail's API

4. general python techniques
   - lambda functions
   - f strings or .format for html formatting
   - using lists of dictionaries

### Design

#### GUI

The Graphical User Interface of this app is built using Python's Tkinter module, which includes several widgets such as entry boxes, labels and buttons. The PNG cat image is imported via Pillow, which has a ImageTk class to manipulate images.

There are 3 functions related to the GUI interface:

1. clear_entry(): clears placeholders in entry boxes when clicked
2. countdown(): initializes the countdown and displays it continuously.
3. button_command(): resets all the dynamic content, checks user input variables, and calls the main program functions.

The organization of the GUI was achieved using the .grid() format, which places widgets within invisible rows and columns. It should be noted that on my system (2009 MacBook running El Capitan) much of the formatting options in Tkinter did not work/display properly.

#### Webscraping

A separate function was made for scraping Kijiji and Amazon respectively, in order to create more modularity and options for the user. Much of the code is similar between the two functions.

To begin, the user input search terms are split into their individual words, and added to the base URL in the pattern of the target websites design. Kijiji's URL contains location specific information, so the GTA (Greater Toronto Area) is used for this app by default. The completed URL is then accessed with the requests module, and then queried/parsed using BeautifulSoup and lxml parser.

BeautifulSoup is used to find target HTML elements (identified manually via the developer tab on the browser) to systemically reduce the HTML of the page to only the relevant parts. From this reduced HTML, individual data such as the price, title, etc can be parsed out and stored in variables. For each item that is webscraped, the item's properties are stored in a dictionary, which is then appended to a list of dictionaries. The list is then sorted by the price key of the dictionary entries, and returned.

#### Emailing

The auto_email() function connects to the Gmail email server, using Gmail's API and the smtplib module. The email and password associated with the Gmail account that sends the email are stored locally in environmental variables (stored in PATH) to keep them hidden and secure. Note that to automatically send emails using Gmail's API, you must first unable access to "less secure" 3rd party apps. Follow the Gmail documentation for this.

A plain-text and an HTML email option are prepared here, to cover both options in case the end user is configured to only receive plain text emails. For the HTML email, each value from each dictionary in the returned lists from the webscraping functions is added to a row of an HTML table, along with appropriate headings. The email is then sent to the user inputted email address. If there is any issues connecting to the server or sending the email, an exception message is printed to the terminal and the GUI.

### Opportunities for Improvement

- not importing modules with \* wildcard - cleaner/clearer code when prefixes are added
- adding a button to end countdown loop
- using HTTP sessions during webscraping to track cookies and prevent being blocked by the target websites
- breaking code into more separate functions. I struggled passing variables around, particularly with the infinite loop of the GUI
- better formatting of prices (include cents, sort list even with non-numerical entries)
- adding an option to change location
- adding an option to track prices over time (perhaps add to SQL database or CSV)
