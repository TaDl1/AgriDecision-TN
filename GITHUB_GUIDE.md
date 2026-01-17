# How to Push Your Project to GitHub

Since you already have the code locally, follow these steps to get it onto GitHub.

## Step 1: Initialize Local Git Repository (If not already done)
The `AgriDecision-TN` folder is already a git repository so you can skip `git init`.

## Step 2: Commit Your Code
I have configured a `.gitignore` file to exclude temporary files. Run these commands in your terminal to save your current work:

```bash
git add .
git commit -m "Initial commit for AgriDecision-TN"
```

> **Note:** If this is your first time using Git, you might see an error asking for your email/name. Run these commands if needed:
> ```bash
> git config --global user.email "you@example.com"
> git config --global user.name "Your Name"
> ```

## Step 3: Create a Repository on GitHub
1.  Go to [github.com](https://github.com) and log in.
2.  Click the **+** icon in the top-right corner and select **New repository**.
3.  **Repository name:** `AgriDecision-TN`
4.  **Description:** (Optional) "Prescriptive agricultural platform for Tunisia."
5.  **Visibility:** Choose **Public** or **Private**.
6.  **Initialize this repository with:** **DO NOT** check any boxes (Readme, gitignore, license). You want an empty repo.
7.  Click **Create repository**.

## Step 4: Link and Push
Once created, GitHub will show you a page with commands. Look for the section **"…or push an existing repository from the command line"**.

Copy and run those commands. They will look like this:

```bash
git remote add origin https://github.com/YOUR_USERNAME/AgriDecision-TN.git
git branch -M main
git push -u origin main
```

## Step 5: Verify
Refresh the GitHub page. You should see all your files (backend, frontend, reports, etc.) listed there!
