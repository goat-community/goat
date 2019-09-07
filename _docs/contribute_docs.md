---
title: Making changes on the Docs
permalink: /docs/contribute_docs/
---

GOAT<sub>beta</sub> is an open source project. Not only can you use it - you can also help improve it. If you have suggestions for improving this Docs site, you are welcome to incorporate them and push them to github. This documentation will show you in detail, how this works. 

The website programming is done in HTML and CSS.

#### 1. Get a fork of GOAT

To make changes on the GOAT<sub>beta</sub> repository it is easiest to first get a personal copy (called <i>fork</i>) of it. In your personal fork you can freely experiment with changes without affecting the original online website. The changes will only become visible online when they are sent via pull-request to the owner of the origin repository and accepted by him. 

Go to [https://github.com/EPajares/goat/](https://github.com/EPajares/goat/) and press the "Fork" button. 

<img class="img-responsive" src="../../img/git_fork.png" alt="how to get a fork of GOAT" title="Get a fork of GOAT"/>

Your now have a personal repository of GOAT on github. 

#### 2. Download your repository

Download your GOAT repository from github by pressing the "Clone or download" button.

<img class="img-responsive" src="../../img/git_download_personal_repository.png" alt="how to get a fork of GOAT" title="Get a fork of GOAT"/>

#### 3. Change to the "gh-pages" branch

Then open a new console window, go into the folder of your GOAT repository and change to the "gh-pages" branch, where the website documents are stored:

`git checkout gh-pages`

#### 4. Define your git remote origin and upstream

To connect the downloaded repository on your computer with the online repositories on github, you have to define the git remote origin and upstream address. 

`git remote add origin https://github.com/YOUR_REPOSITORY.git`

`git remote add upstream https://github.com/EPajares/goat.git`

<i> Origin </i> represents your personal GOAT repository, where you can freely experiment with changes, and <i> upstream </i> represents the website owner's repository, which builds the original website.

With the following command you can check the stored origin and upstream addresses:

`git remote -v`

#### 5. Make sure to have the newest file versions

Before making any changes, it makes always sense to check if your local repository is up to date with the upstream repository.

...






#### 6. Make your changes

All the markdown files of the website are stored in the "_docs" folder. It is recommended to open the files with a proper editor such as [Visual Studio Code](https://code.visualstudio.com/). Now you can edit the files and make the desired changes to improve the GOAT<sub>beta</sub> Docs. 

#### 7. View your changes on a local website

You can view your changes on a local website by executing the following command:

`bundle exec jekyll serve`

With this command, [Jekyll](https://jekyllrb.com/) creates a local website using the programming language [Ruby](https://www.ruby-lang.org/en/). You can access it by typing the following into your browser: 

[http://localhost:4000](http://localhost:4000)

This website is updated every few seconds (make sure to refresh the page to see your latest changes).

#### 8. Push your changes to your personal GOAT repository on github

#### 9. Make a pull request