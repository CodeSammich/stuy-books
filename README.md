# stuy-books
Book marketplace for Stuyvesant High School

> "I would like to have a marketplace for students to buy and sell books, which I understand students currently do through the 'Facebooks' and the 'tweets'. If I were a student, I would not just like to find a book, but for a book of mine to be recognized."

### Live Link Deployed at StuyCS.org
http://stuybooks.stuycs.org

### Setup Instructions
1. Clone `stuy-books`
    
	    git clone https://github.com/CodeSammich/stuy-books.git   // https cloning
		git clone git@github.com:CodeSammich/stuy-books.git       // ssh cloning

2. Install MongoDB

###### Windows
		Download MongoDB for Windows here:
		https://www.mongodb.com/download-center#community
		
> In Windows Explorer, locate the downloaded MongoDB .msi file, which typically is located in the default Downloads folder. Double-click the .msi file. A set of screens will appear to guide you through the installation process. 
You may specify an installation directory if you choose  installation option.  
__NOTE:__  
	These instructions assume that you have installed MongoDB to `*C:\mongodb*`.  
	MongoDB is self-contained and does not have any other system dependencies. You can run MongoDB from any folder you choose. You may install MongoDB in any folder (e.g. `*D:\test\mongodb).Customthe*`  
  	For more information: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/
		
###### Mac OSX
		
		brew install mongodb     // requires Homebrew
		
###### Ubuntu 14.04

		sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
		echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
		sudo apt-get update
		sudo apt-get install -y mongodb-org
		
		For more information and version-specific installation, please visit our friends at MongoDB:
		https://docs.mongodb.com/manual/administration/install-on-linux/		
		
3. Install and run Flask
4. Install pymongo `pip install pymongo`
5. Download the "password.txt" file that we will email you, and place it in the root of the repository
6. Use the Google OAuth Client Key that we will email you in the indicated places in:
   - "templates/base.html" 
     - line 23 at `<!-----------------------------------GOOGLE CLIENT ID---------------------------------------->`
   - "templates/login.html" 
     - line 10 at `<!-----------------------------------GOOGLE CLIENT ID---------------------------------------->`
	 - line 22 at `//<!-----------------------------------GOOGLE CLIENT ID---------------------------------------->//`

7. Run installed packages:

##### MongoDB

###### Windows
###### Mac OSX
###### Ubuntu 14.04
	
		sudo service mongod start                                   //to start MongoDB
		[initandlisten] waiting for connections on port <port>      //to verify that MongoDB has started successfully
		
		sudo service mongod stop                                    //to stop MongDB
		
		sudo service mongod restart                                 //to stop MongoDB
		
### The Team!

|                                       |   **Member**   |                   **GitHub**                 |            **Role**            |
|---------------------------------------|:--------------:|:--------------------------------------------:|:------------------------------:|
| <img src="images/amanda.jpg" width="100" height="100" /> | Amanda Chiu   |[`@amandalchiu`](https://github.com/amandalchiu)        | Frontend |
| <img src="images/helen.jpg" width="100" height="100" /> | Helen Li   |[`@lihelennn`](https://github.com/lihelennn)        | Middleware / API-Handler  |
| <img src="images/samuel.jpg" width="100" height="100" /> | Samuel Zhang |[`@CodeSammich`](https://github.com/CodeSammich)    | Middleware/Backend - Leader  |
| <img src="images/jeff.jpg" width="100" height="100" /> | Jeffrey Zou    |[`@JeffreyZou13`](https://github.com/JeffreyZou13)| Backend |

### Daily Agenda

##### Agenda for 6/10/16:

- Frontend/middle
- Middleware
  - [ ] Deployment implementation
- Backend:
  - [ ] Search Engine Optimization

### The Future
[with notes from final client meeting on 6/10/16]

- Waiting queue for pictures 
(to filter inappropriate listings from showing)
- Reminder emails if *x* number of days pass and meeting has not been confirmed
(incorporate time stamps for each listing into database)
- Historical archive for site managers (oversight of all transactions)
- (in 'Past Transactions') add the person/user who you had transaction with

- Rating (stars) system for sellers
  - profile pages for users to see other users / rate
  - link in email to rate the transaction/user
  - Individual ratings listed on book pages
  - instanced profile pages for other users (to see another user's transactions, etc.)
  - search engine for users and books + filters
    - filter by highest rated, lowest rated, users, etc.
	
### Dev-log

##### 6/09/2016
- Google signin redirects and only works when button is clicked.
- Only stuy.edu emails can sign up and log in.
- Different pages (such as search, remove, edit, etc.) added and prettified.
- GO TEAM JASH!

##### 5/31/16
- Google Signin works -- needs to redirect
- Search engine fixed -- needs to be optimized
- Flow chart created in class
- Tooltips for signup/forms


##### 5/27/16
- Backend search engine function working properly
- Search engine connected to some of the front end pages
* Confirmation page functional and secure

##### 5/26/16
- Added remove functionality for backend databases
- Added auto-email functionality
- Confirmation link not yet functional/secure

##### 5/25/16
- Added image to listings
- Improved visual presentation of pages (and listings) after login

##### 5/22/16
- Added login functionality
 - user databases, books database/structure

##### 5/19/16
- Added pages for home, login, signup, sell/buy, master book list
- middleware integration with html/css

## Original Plans + Ideas
- Serial number, verify the actual book manually previously
- Automated search and verification of a book automatically (current eBay model)
- Tied to school email account
  - Simple response: "Good or bad"
  - Too long rating is a deterrant
    - Simplicity for rating on a seller/buyer for reputation
	- Preventing/reducing "no-show"
	  - Not so much dangerous for Stuyvesant students
  - Choose between multiple buyers with higher reputation
  - Anonmyous UNTIL buyer/seller confirms to _avoid_ personal bias: _only sees buyer names (maybe photos/avatar) after confirmation_
- May have a shortlist of proposed meeting spots in school: pre-offering meeting spots for security and community streamline reasons
  - Facilitating timely exchanges
- Any sort of known textbook, can request, buy, and offer to sell
  - A finite list of Barron's, Kaplan
  - What book within what topic, etc.
  - "Here are the list of textbooks we offer at this school"
- Emphasize fair trading and fair value rather than auction*
  - Reduces waste of textbooks that people no longer need
- Clear choice between Buyer/Seller option at the beginning of the website
- Comment section/forum for peer confirmation**

##### Expansions
- Study guide compilation (Midnightswan)
- Calculator marketplace, etc.
  - *Suggested Amount*: "Similar items have been sold for __ amount"
- Notifications on smart device

** Not initial feature, may devolve into irrelevant chat **

