---
title: Contribute to the documentation
permalink: /docs/contribute_docs/
---

GOAT is an open source project. You can not only use it, but you are also very welcome to contribute. Besides contributing code or collecting OpenStreetMap data, you can also help improving our documentation. This website is hosted on Github with the rest of the GOAT codebase and is using [Jekyll](https://jekyllrb.com/) as static site generator. This allows to build a website with the markdown language based on templates.

In order to contribute to the website you will need to have a code editor, Git and Jekyll installed, furthermore you need a Github-Account.
The following steps show one possible workflow to contribute to the website. 

#### 1. Get a fork of GOAT

To make changes to the GOAT repository the easiest way is to first get a personal copy (called <i>fork</i>) of it. In your personal fork you can freely experiment and also push your changes to your own GitHub account.

Go to [https://github.com/goat-community/goat](https://github.com/goat-community/goat) and press the "Fork" button. 

<img class="img-responsive" src="../../img/git_fork.png" alt="how to get a fork of GOAT" title="Get a fork of GOAT"/>

You now have a personal fork of the GOAT respository on GitHub.

#### 2. Create a local clone of your GOAT repository

Navigate to your fork of the GOAT repository. Press the "Clone or download" button and copy the clone URL.

<img class="img-responsive" src="../../img/git_clone_personal_repository.png" alt="how to clone your fork of the GOAT repository" title="Get a clone of your GOAT repository"/>

Open Git Bash, go to the directory where you want to store the repository and clone it using the copied URL:

`git clone https://github.com/YOUR_USERNAME/goat.git`

#### 3. Define your git remote origin and upstream

In order to fetch changes done by other users frequently, it is recommended to add the original repository as remote. Direct to the GOAT folder you just downloaded and check the stored origin and upstream addresses:

`cd goat`

`git remote -v`

So far, the GitHub URL of your GOAT repository should be listed as <i> origin</i>. To later fetch from the original repository of the website you have to define the GitHub URL of the GOAT respository as <i> upstream</i>: 

`git remote add upstream https://github.com/goat-community/goat.git`

#### 4. Change to the "website-development" branch

Change to the "website-development" branch, at this branch the development version of the website is stored:

`git checkout website-development`

If you receive an error message that this branch does not yet exist, visit the GitHub website, navigate to your repository and create a new branch called "website-development".

#### 5. Make sure to have the newest file versions

Before making any changes, it makes always sense to ensure your local repository is up to date with the upstream repository.

First, check if you have any previous changes which have not been uploaded yet:

`git status`

Then get the newest version of the upstream repository:

`git fetch upstream`

Merge the new version of the website-development branch into your current branch:

`git merge upstream/website-development`

Push the new version to your origin GitHub repository:

`git push origin`

Now you are ready to contribute.

#### 6. Make your changes

All the markdown files of the website are stored in the "_docs" folder. It is recommended to open the files with a proper editor such as [Visual Studio Code](https://code.visualstudio.com/). You can edit the files and make the desired changes to improve the GOAT Docs.

#### 7. View your changes on a local website

You can view your changes on a local website by executing the following command:

`bundle exec jekyll serve`

With this command, [Jekyll](https://jekyllrb.com/) creates a local website using the programming language [Ruby](https://www.ruby-lang.org/en/) (if Jekyll is not yet installed on your computer, it can be downloaded [here](https://jekyllrb.com/docs/installation/)). 

You can access the local website by typing the following into your browser: 

[http://localhost:4000](http://localhost:4000)

The website is updated if you change one of the files (make sure to refresh the page to see your latest changes).

To stop local server, press CTRL + C and confirm. 

#### 8. Push your changes to your origin repository

If you are done with your changes, you can commit your changes and comment what you have done:

`git add .`

`git commit -m 'COMMENT'`

Push your changes to your origin repository on GitHub:

`git push`

#### 9. Make a pull request

When you have finalized your changes and are completely satisfied with them, you can send a pull request to the website owner.

Push the new version to your origin GitHub repository:

`git push origin website-development`

Go on GitHub, navigate to your fork of the GOAT repository. There you can see your recently pushed branches. Click on "Compare & pull request" for the branch you want to commit.

<img class="img-responsive" src="../../img/git_pull_request.png" alt="how to make a pull request to the original GOAT repository" title="Make a pull request"/>

Explain in detail what you have done and submit it by pressing the button "Create pull request".

Your changes will now be reviewed, if everything is fine they will be soon visible online on the website or you will be asked to refine your changes.

