# Unilexicon: taxonomy editor and tagging suite

<https://unilexicon.com>

Visual tool for managing controlled vocabularies

:   -   uses hypertree graphs to allow users exploring and editing
        vocabularies
    -   helps users to comprehend relations in large taxonomies

Tagging tool for tagging resources using controlled vocabularies

:   -   use controlled vocabularies from the repository to tag your
        resources and web pages
    -   works contextually as a Chrome browser extension

## Content findability toolkit

Aiding data exchange, categorisation, classification and searching.

Create, Export, Import, Explore, Manage, Iteratively improve

-   Vocabulary, Classification, Taxonomy
-   Tagging in context

Standard technology: HTML+CSS+JS, Python

Standard formats: SKOS, JSON, Excel/CSV

## Server Installation - Vocabulary editor & repository

Install Python, MySQL or your database of choice and all required
packages.

> pip install -r requirements.txt

Create database and add name, user and password to settings_local.py
based on the text template provided.

Run:

> ./manage.py migrate ./manage.py runserver

For MySQL enable fulltext indexes.

> ALTER TABLE concepts ADD FULLTEXT(name); ALTER TABLE concepts ADD
> FULLTEXT(description);

Import SKOS vocabularies from disk (or upload them later):

> ./manage.py load_skos -r \<directory of the vocabularies to import
> e.g.: /path/to/vocabs/\>

## Browser Installation - Tagging tool

User: In Chrome browser go to your vocabulary editor \> click tagging \>
Install.

Developer: hit Wrench \> Tools \> Extensions \> Expand + Developer Mode
\> Load unpacked extension \> Choose folder to load sources from. It
should be ./tag/

## Credits
 - Web framework (Templates, ORM, MVC) used is [Django](https://djangoproject.com) with Gunicorn a deployment backend server.
 - PyMySQL and mysqlclient are database bindings for MySQL being phased out for Postgres.
 - xlrd used to read Excel files, lxml helps parse DM+D medd export data with fabric automating updates.
 - Sentry_sdk is used for error reporting.
 - Graph visualisation uses [The JavaScript InfoVis Toolkit](https://github.com/philogb/jit).
 - Frontend Javascript uses [jQuery](https://jquery.com) and jQuery UI being phased for modern vanilla JS.

## Keywords

-   taxonomy software
-   thesaurus software
-   visual thesaurus
-   thinkmap visual thesaurus
-   open source taxonomy management
-   ontology software
-   classification software
-   SKOS editor
-   online taxonomy software
-   classification software

## Deployment notes

Static media files are served using Nginx, which serves as a reverse
proxy. It sends requests for paths that do not exist on the disk to
Gunicorn server.

Gunicorn listens on port 8080. nginx.conf proxy_pass is set to 8000
django dev server, so this needs changing for deployment.

Another important bit of the config file is:

> add_header Access-Control-Allow-Origin\...

This allows the Chrome tagging extension to get on with the AJAX Cross
Site Scripting(XSS) security controls.

## Tagging extension

Tagging extension for Google Chrome has a bit of configuration on top of
the tag.js file. Unpacked code is in the /tag folder.

## Dual Licensing

### Commercial license

If you want to use Unilexicon to develop and run commercial projects and
applications, the Commercial license is the appropriate license. With
this option, your source code is kept proprietary.

Once purchased, you are granted a commercial BSD style license and all
set to use Unilexicon in your business.

[Small Team License
(£2500)](https://unilexicon.com/fm/pay.html?amount=2500&msg=Unilexicon_Team_License)
Small Team License for up to 8 developers

[Organization License
(£4500)](https://unilexicon.com/fm/pay.html?amount=4500&msg=Unilexicon_Organization_License)
Commercial Organization License for Unlimited developers

### Open source license

If you are creating an open source application under a license
compatible with the GNU GPL license v3, you may use Unilexicon under the
terms of the GPLv3.

## TODO

- collaboration features
    - cooperative mode
    - change list attributed to users
      "x" was rename to "y" (by user) _restore_
    - undo / redo; approve / cancel
- i10n / l10n
- introductory video
- tag tool with API on Chrome app store
- alternative UI
- support custom relation types for ontologies

See https://github.com/fmalina/unilex/issues
