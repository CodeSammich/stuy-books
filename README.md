### Setup Instructions
1. Clone the project
2. Install and run Mongo
3. Install and run Flask
4. Download the "password.txt" file that we will email you, and place it in the root of the repository
5. Use the Google OAuth Client Key that we will email you in the indicated places in "base.html" (line 23) and "login.html" (line 10 and line 22)

|                                       |   **Member**   |                   **GitHub**                 |            **Role**            |
|---------------------------------------|:--------------:|:--------------------------------------------:|:------------------------------:|
| <img src="images/amanda.jpg" width="100" height="100" /> | Amanda Chiu   |[`@amandalchiu`](https://github.com/amandalchiu)        | Frontend |
| <img src="images/helen.jpg" width="100" height="100" /> | Helen Li   |[`@lihelennn`](https://github.com/lihelennn)        | Middleware / API-Handler  |
| <img src="images/samuel.jpg" width="100" height="100" /> | Samuel Zhang |[`@CodeSammich`](https://github.com/CodeSammich)    | Middleware/Backend - Leader  |
| <img src="images/jeff.jpg" width="100" height="100" /> | Jeffrey Zou    |[`@JeffreyZou13`](https://github.com/JeffreyZou13)| Backend |

### Daily Agenda

##### Agenda for 6/2/16:

- Frontend/middle: (Everything else is Helen + Sam)
	- [x] Redirection from google sign-in (update: redirects to "/index")
	- [x] Start adding buttons for login pages for
		- [x] "Transaction complete",
		- [x] "Remove book from list",
		- [x] "Edit book information"
		- [x] Prettiness of the buttons above
	- [x] book status ( Available, Pending, Sold ),
	- [x] Prettiness *(Amanda)*
	- [x] Tooltip For Signup *(Amanda)*
	- [x] When screen is sized down, enabled side scrolling instead *(Amanda)*
	- [x] Run properly in Firefox, Chrome, and Safari *(Amanda)*
- Middleware
	- [x] Username properly display on all pages (instead of "Username")
	- [x] Books should have different prices, conditions but one entry listed after search
	 - [x] One buy page per book with name and seller email
- Backend:
	- [x] Email both parties after "buy button" + books status in book object,
	- [x] Finish transaction
	- [x] Send email to both client and buyer
	- [x] NO REPEAT ENTRIES UNLESS PRICE/CONDITION IS DIFFERENT
	- [x] All database calls should use name, seller, price and condition
	- [x] Edit book information
	- [x] Search Engine Optimization
	- [x] Cancel Transaction (same mechanism as Finish)

 - [x] User frees information

> Remember, each user is both a buyer AND a seller.




# stuy-books
Book marketplace for Stuyvesant High School

> "I would like to have a marketplace for students to buy and sell books, which I understand students currently do through the 'Facebooks' and the 'tweets'. If I were a student, I would not just like to find a book, but for a book of mine to be recognized."

## Members
| Name        | Github           |
| ------------- |:-------------:|
| Amanda Chiu  | [amandalchiu](https://github.com/amandalchiu)           |
| Helen Li    | [lihelennn](https://github.com/lihelennn)      |
| Samuel Zhang |[CodeSammich](https://github.com/CodeSammich)  |
| Jeffrey Zou |[JeffreyZou13](https://github.com/JeffreyZou13) |

### Original Plans + Ideas
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

### To-Do
> To be updated with Client meeting notes
- OAuth authentication, confirmation emails
- Buy functionality (email sending)
- Database handling "remove", "Schrodinger pending state for books", front-end implementation of pending
- Optimizing search engine/picture search (have an autocomplete functionality)
- Disclaimers + misc. issues
- Finding books by ISBN number
- A flow chart of what the user should see, depending on if he/she is a buyer or seller
- An email to Mr. Brown about a To-Do List with prioritization
- A report for buyers/sellers about transactions made this month, their ratings, etc.
- A list of places to meet
	- Outside the library
	- Senior or sophomore bar
	- Half floor
	- Outside the theater
- Message to the users about proper beheavior

### Dev-log
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
