Unilexicon: taxonomy editor and tagging suite
=============================================
https://unilexicon.com

Visual tool for managing controlled vocabularies
 - uses hypertree graphs to allow users exploring and editing vocabularies
 - helps users to comprehend relations in large taxonomies

Tagging tool for tagging resources using controlled vocabularies
 - use controlled vocabularies from the repository to tag your resources and web pages
 - works contextually as a Chrome browser extension

Content findability toolkit
---------------------------
Create, Export, Import, Explore, Manage, Iteratively improve

- Vocabulary, Classification, Taxonomy
- Tagging in context
 
Standard technology: HTML+CSS+JS, Python

Standard formats: SKOS, JSON, Excel/CSV

Server Installation - Vocabulary editor & repository
----------------------------------------------------
Install Python, MySQL or your database of choice and all required packages.

   pip install -r requirements.txt

Create database and add name, user and password to settings_local.py based on the text template provided.

Run:

    ./manage.py migrate
    ./manage.py runserver

For MySQL enable fulltext indexes.

    ALTER TABLE concepts ADD FULLTEXT(name);
    ALTER TABLE concepts ADD FULLTEXT(description);

Import SKOS vocabularies from disk (or upload them later):

    ./manage.py load_skos -r <directory of the vocabularies to import e.g.:  /path/to/vocabs/>

Browser Installation - Tagging tool
-----------------------------------
User: In Chrome browser go to your vocabulary editor > click tagging > Install.

Developer: hit Wrench > Tools > Extensions >
Expand + Developer Mode > Load unpacked extension >
Choose folder to load sources from. It should be ./tag/

Credits
---------
+---------------------+----------+-------------------+
| Graph visualisation | the Jit  | thejit.org        |
+---------------------+----------+-------------------+
| Templates, ORM, MVC | Django   | djangoproject.com |
+---------------------+----------+-------------------+
| Frontend JS         | jQuery   | jquery.com        |
+---------------------+----------+-------------------+
| Icons               | jQuery UI| ui.jquery.com     |
+---------------------+----------+-------------------+

Keywords
--------
- taxonomy software
- thesaurus software
- visual thesaurus
- thinkmap visual thesaurus
- open source taxonomy management
- ontology software
- classification software
- SKOS editor
- online taxonomy software
- classification software


Deployment notes
----------------
Static media files are served using Nginx, which serves as a reverse proxy.
It sends requests for paths that do not exist on the disk to Gunicorn server.

Gunicorn listens on port 8080.
nginx.conf proxy_pass is set to 8000 django dev server,
so this needs changing for deployment.

Another important bit of the config file is:

    add_header Access-Control-Allow-Origin...

This allows the Chrome tagging extension to get on with the AJAX
Cross Site Scripting(XSS) security controls.


Tagging extension
-----------------
Tagging extension for Google Chrome has a bit of configuration on top of the
tag.js file. Unpacked code is in the /tag folder.
