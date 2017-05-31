===============
Getting started
===============

Once you have signed in for the first time, you need to connect GitHub with the workbench, so that users can use all the features.


Change your admin password
==========================
Change your administrator password via the /admin, at the top right you have the option Change password. Make sure to properly secure the admin user account, as this account can view all the GitHub tokens from the users and thus should be handled with care.

Connect to GitHub
=================
You can retrieve a Client ID and Client Secret needed to connect with GitHub by going to your GitHub personal settings, OAuth applications and create a new app. Set the Homepage URL to your website and set the Authorization Callback URL to: http://yourdomain/accounts/github/login/callback/.

Go to the admin section of the workbench (/admin) and open the model Social applications.
Here, create a new Social application named GitHub and enter your Client ID and Client Secret that you have retrieved just now.

