About project structure
-----------------------

In flask it is possible to do both, backend and frontend of the website. 
If we start from the direction frontend to backend, 
the first thing you can look at is __templates__ folder. 
There are stored HTML codes. 
They use Jinja templating engine, 
which means that it is possible to separate different parts of webpages into smaller parts. 
For example if we render the home page, 
the look of the website is defined in __base.html__ 
which imports __home.html__.
In __base.html__ there is only placeholder for content. 
__home.html__ contains another placeholder for footers for example. 
These templates are rendered from __views__ folder. 
View is basically an URL address 
and in a view we specify which variables will be used for rendering a specific template. 
Views can also use formulars which are defined in __forms__ folder. 
The database and the initial data are stored in the __data__ folder. 
Models (tables in the database) are stored in __models__ folder.
In the __static__ folder we store static content, images etc.
Functions which do not belong into any of those folders, 
but are needed are defined in __common__ folder.

Inside this folder
------------------

- \_\_init\_\_.py - Initializes the app, imports all flask add-ons
- templates - HTML codes using Jinja for look of the webpage
- views - Define variables and commands to render a specific template with them
- forms - Formulars used in views
- data - Database and initial data are stored here
- models - Tables in the database are specified here
- static - Contains static content of the app
- common - Various functions used through the code
