---
sidebar_position: 1
slug: /
---

import docusaurusImg from "/img/docusaurus.png"
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Getting started

<div style={{display: "flex", justifyContent: "center"}}>
  <img src={docusaurusImg} style={{width: "100px"}}/>
</div>

<Tabs>
  <TabItem value="apple" label="Apple" default className="tabItemBox">
    This is an apple 🍎
  </TabItem>
  <TabItem value="orange" label="Orange" className="tabItemBox">
    This is an orange 🍊
  </TabItem>
  <TabItem value="banana" label="Banana" className="tabItemBox">
    This is a banana 🍌
  </TabItem>
</Tabs>

This is <span style={{color: "#FF0000"}}>red</span> and this is <span style={{color: "#FFFF00"}}>yellow</span>

Let's discover **Docusaurus in less than 5 minutes**.

## Getting Started

Get started by **creating a new site**.

Or **try Docusaurus immediately** with **[docusaurus.new](https://docusaurus.new)**.

### What you'll need

- [Node.js](https://nodejs.org/en/download/) version 16.14 or above:
  - When installing Node.js, you are recommended to check all checkboxes related to dependencies.

## Generate a new site

Generate a new Docusaurus site using the **classic template**.

The classic template will automatically be added to your project after you run the command:

```bash
npm init docusaurus@latest my-website classic
```

You can type this command into Command Prompt, Powershell, Terminal, or any other integrated terminal of your code editor.

The command also installs all necessary dependencies you need to run Docusaurus.

## Start your site

Run the development server:

```bash
cd my-website
npm run start
```

The `cd` command changes the directory you're working with. In order to work with your newly created Docusaurus site, you'll need to navigate the terminal there.

The `npm run start` command builds your website locally and serves it through a development server, ready for you to view at http://localhost:3000/.

Open `docs/intro.md` (this page) and edit some lines: the site **reloads automatically** and displays your changes.
