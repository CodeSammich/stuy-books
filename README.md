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
- buy functionality (email sending)
- Tooltips for signup/forms
- Database handling "remove", "Schrodinger pending state for books", front-end implementation of pending 
- Optimizing search engine/picture search
- Disclaimers + misc. issues


### Dev-log
##### 5/27/16
- Backend search engine function working properly
- Search engine connected to some of the front end pages

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
