---
description: "Manage team members, share datasets, projects and folders with people, teams or the organization, transfer ownership to a team, and restore deleted items from the Trash."
sidebar_position: 1
---

# Teams & Members

Sharing datasets and projects allows for a more efficient workflow because **granting access to other members enables them to simultaneously edit and/or view your datasets or projects**. 

::::info
Sharing **does not duplicate** your data, only grants access to it.
::::



## Managing Teams and Members

<div class="step">
   <div class="step-number">1</div>
   <div class="content">Go to the <code>Settings</code> section.</div>
</div>

<div class="step">
   <div class="step-number">2</div>
   <div class="content">Click on a <code>Team</code> and <b>view the list of Teams</b> you are part of. Teams can represent departments or groups within your organization.</div>
</div>
<div class="step">
   <div class="step-number">3</div>
   <div class="content">Then click on the <code>Members</code> tab to <b>see the members and their roles</b>.</div>
</div>

<div class="step">
   <div class="step-number">4</div>
   <div class="content">
   If you are the <b>Owner</b> of the Organization, you can:
      <ul>
         <li>Click <code>+ New Member</code> to add a new member.</li>
         <li>Click the <code>More Options</code> <img src={require('/img/icons/3dots.png').default} alt="More options" style={{ maxHeight: '20px', maxWidth: '20px', verticalAlign: 'middle'}}/> menu and then on <code>Delete</code> to remove a member</li>
      </ul>
   </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/manage_team_members.webp').default} alt="Managing team members in Settings" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "contain"}}/>
</div>
<p> </p>

:::important
When you share a dataset/project with a Team/Organization, all members will have access to it.
:::

---

## Managing access to a Dataset, Project, or Folder

Open the item's <code>More Options</code> <img src={require('/img/icons/3dots.png').default} alt="More options" style={{ maxHeight: '20px', maxWidth: '20px'}}/> menu and select <code>Share</code>. The dialog has these tabs:

- **People**: share a **dataset, project or template** with an **individual person** from your organization. Search for them; the item appears in their `Shared with me` and stays where it lives. Folders and bundles can only be shared with teams and the organization.
- **Teams**: share with a whole **Team or Organization**. Grant its members <code>Viewer</code> or <code>Editor</code> access, or <code>No Access</code> to withdraw it.
- **Public** (datasets and projects only): for a **dataset**, make it public to all GOAT users; for a **project**, publish a public web snapshot that anyone can open without a GOAT account. Both are covered in [Public Sharing](./public.md).

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/share_dialog_tabs.webp').default} alt="Opening Share and the People, Teams and Public tabs" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "contain"}}/>
</div>
<p> </p>

:::info
To withdraw access, open the <code>Share</code> dialog again and set the role back to <code>No Access</code>.
:::

### Sharing a Folder

You can also share an entire **folder** at once. Sharing a folder grants access to **all datasets and projects inside it**, so you don't have to share each item individually.

<div class="step">
   <div class="step-number">1</div>
   <div class="content">Click the <code>More Options</code> <img src={require('/img/icons/3dots.png').default} alt="More options" style={{ maxHeight: '20px', maxWidth: '20px'}}/> menu on a folder you own and select <code>Share</code>.</div>
</div>
<div class="step">
   <div class="step-number">2</div>
   <div class="content">Choose an <code>Organization</code> or <code>Team</code> and grant <code>Viewer</code> or <code>Editor</code> access as needed.</div>
</div>

:::info
A folder can be shared with several teams and the organization at the same time. Items inside a shared folder inherit the folder's access, so sharing them individually is not needed.
:::

### Accessing Shared Items

Everything shared with you, personally or through a team or the organization, appears under <code>Shared with me</code> in the <code>Spaces</code> panel of [Content](../workspace/content.md).


## Transferring ownership

You can **hand an item over to a team or organization** so that it no longer belongs to you personally. This works for datasets, projects, folders, bundles and templates that you own in your **My Content**; for items in a team or organization space, the option does not appear. [Content](../workspace/content.md#sharing-and-transferring-are-different) explains how this differs from sharing.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/transfer_ownership.webp').default} alt="Transfer ownership on the Teams tab of the Share dialog" style={{ maxHeight: "480px", maxWidth: "480px", objectFit: "contain"}}/>
</div>
<p> </p>

<div class="step">
   <div class="step-number">1</div>
   <div class="content">Open the item's <code>More Options</code> <img src={require('/img/icons/3dots.png').default} alt="More options" style={{ maxHeight: '20px', maxWidth: '20px'}}/> menu, choose <code>Share</code> and open the <code>Teams</code> tab. In the <code>Transfer Ownership</code> row, click <code>Transfer…</code>.</div>
</div>
<div class="step">
   <div class="step-number">2</div>
   <div class="content">Under <code>To</code>, pick the team or organization that should own the item.</div>
</div>
<div class="step">
   <div class="step-number">3</div>
   <div class="content">For a project, choose <strong>which datasets move along</strong> with it: every dataset you own starts out ticked, so untick the ones you want to keep. Datasets owned by others can't be ticked. Ticked datasets become the team's too, so the project never loses them when you leave. Unticked ones <strong>stay where they are</strong>, and the team keeps seeing them through the project.</div>
</div>
<div class="step">
   <div class="step-number">4</div>
   <div class="content"><code>Leave a shortcut in the old location</code> is on by default, so the item stays reachable from where it was. Turn it off if you don't want one, then confirm the transfer.</div>
</div>

After a transfer:

- The item leaves your **My Content** and the team (or organization) owns it. It stays with the team even if you later leave it.
- **Everyone in that team or organization gets access.** Personal shares with individual people are removed, since space membership takes over.
- Datasets still **used by projects elsewhere keep read access**, so those projects keep working.

:::info
Transferring ownership changes who the item belongs to and replaces its personal shares. If you only want to give others access without handing it over, use <code>Share</code> instead.
:::

## Trash

Deleted items are not removed immediately. They **go to the Trash first**.

Each space has its own Trash. In <code>Content</code>, select a space in the <code>Spaces</code> panel on the left; if you own that space, its <code>Trash</code> appears at the bottom of the panel. Only a space's owner can open its Trash and restore items, so in a team space, ask the team's owner.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/trash.webp').default} alt="Trash at the bottom of the Spaces panel in Content" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "contain"}}/>
</div>
<p> </p>

- Deleting an item moves it to the **Trash**, where it can be **restored for 30 days**.
- Open the Trash to <code>Restore</code> an item, or leave it: items are removed for good **30 days after deletion**.

:::info
When you transfer ownership of a folder, any trashed items inside it move along and stay in the trash.
:::

## Roles

See the table below to learn what each user can do within an Organization/Team and in a shared Dataset/Project:

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/sharing_roles_table.png').default} alt="Roles Table in GOAT" style={{ maxHeight: "Auto", maxWidth: "80%", objectFit: "cover"}}/>
</div>
<p> </p>

:::info Important

Deleting a dataset from a shared project **that you own** removes it *for other users as well*. It goes to your Trash, so you can still restore it within 30 days.
**As an editor** if you delete a dataset or (layer from the) project, the *owner will still have it in their personal dataset*.

:::