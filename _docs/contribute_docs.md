---
title: Making changes on the Docs
permalink: /docs/contribute_docs/
---

GOAT<sub>beta</sub> is an open source project. Not only can you use it - you can also help improve it. If you have suggestions for improving this Docs site, you are welcome to incorporate them and push them to GitHub. This documentation will show you in detail, how this works. 

The website programming is done in HTML and CSS.

#### 1. Get a fork of GOAT

To make changes on the GOAT<sub>beta</sub> repository it is easiest to first get a personal copy (called <i>fork</i>) of it. In your personal fork you can freely experiment with changes without affecting the original online website. The changes will only become visible online when they are sent via pull request to the owner of the origin repository and accepted by him. 

Go to [https://github.com/EPajares/goat/](https://github.com/EPajares/goat/) and press the "Fork" button. 

<img class="img-responsive" src="../../img/git_fork.png" alt="how to get a fork of GOAT" title="Get a fork of GOAT"/>

Your now have a personal fork of the GOAT respository on GitHub. 

#### 2. Create a local clone of your GOAT repository

Navigate to your fork of the GOAT repository. Press the "Clone or download" button and copy the clone URL.

<img class="img-responsive" src="../../img/git_clone_personal_repository.png" alt="how to clone your fork of the GOAT repository" title="Get a clone of your GOAT repository"/>

Open Git Bash, go into the directory where you want to store the repository and clone it using the copied URL:

`git clone https://github.com/YOUR_USERNAME/goat.git`

#### 3. Define your git remote origin and upstream

Then direct into the GOAT folder you just downloaded and check the stored origin and upstream addresses:

`cd goat`

`git remote -v`

So far, the GitHub URL of your GOAT repository should be listed as <i> origin</i>. To later push your changes to the original repository of the website owner, you have to define the GitHub URL of his GOAT respository as <i> upstream</i>: 

`git remote add upstream https://github.com/EPajares/goat.git`

#### 4. Change to the "gh-pages" branch

Change to the "gh-pages" branch, where the website documents are stored:

`git checkout gh-pages`

#### 5. Make sure to have the newest file versions

Before making any changes, it makes always sense to ensure your local repository is up to date with the upstream repository.

First, check if you have any previous changes which have not been uploaded yet:

`git status`

Then get the newest version of the upstream repository:

`git fetch upstream`

Check if you are up to date:

`git checkout gh-pages`

Merge the new version into your gh-pages branch:

`git merge upstream/gh-pages`

Push the new version to your origin GitHub repository:

`git push origin gh-pages`

Now you are ready to contribute.

#### 6. Make your changes

All the markdown files of the website are stored in the "_docs" folder. It is recommended to open the files with a proper editor such as [Visual Studio Code](https://code.visualstudio.com/). You can edit the files and make the desired changes to improve the GOAT<sub>beta</sub> Docs. 

#### 7. View your changes on a local website

You can view your changes on a local website by executing the following command:

`bundle exec jekyll serve`

With this command, [Jekyll](https://jekyllrb.com/) creates a local website using the programming language [Ruby](https://www.ruby-lang.org/en/). You can access it by typing the following into your browser: 

[http://localhost:4000](http://localhost:4000)

This website is updated every few seconds (make sure to refresh the page to see your latest changes).

To stop the batch process, press CTRL + C and confirm. 

#### 8. Push your changes to your origin repository

Commit your changes and comment what you have done:

`git add .`

`git commit -m 'COMMENT'`

Push your changes to your origin repository on GitHub:

`git push`

#### 9. Make a pull request

When you have finalized your changes and are completely satisfied with them, you can send a pull request to the website owner.

First, you need to get the newest version of the upstream repository again:

`git fetch upstream`

Check if you are up to date:

`git checkout gh-pages`

Merge the new version into your gh-pages branch:

`git merge upstream/gh-pages`

Push the new version to your origin GitHub repository:

`git push origin gh-pages`

Go on GitHub, navigate to your fork of the GOAT repository. There you can see your recently pushed branches. Click on "Compare & pull request" for the branch you want to submit.

<img class="img-responsive" src="../../img/git_pull_request.png" alt="how to make a pull request to the original GOAT repository" title="Make a pull request"/>

Explain in detail what you have done and submit it by pressing the button "Create pull request".

If the website owner likes your changes, he will accept them and they will soon be visible online on the website.

