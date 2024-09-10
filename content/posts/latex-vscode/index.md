---
title: "LaTeX in Visual Studio Code (VSCode) on macOS"
date: 2024-09-10T12:48:00+01:00
draft: false

tags:
- writing
- thesis
- vscode
- latex

cover:
    image: "cover.png"
    alt: "Vscode + Latex logo"


---
When writing my thesis I found Overleaf to minimalistic for writing a big project such as an PhD Thesis. Installing LaTeX in Visual Studio Code (VSCode) really helped me so I could work in a modern, customizable text editor. In this post, we'll go through the process of installing LaTeX on macOS using Homebrew, configuring VSCode with LaTeX Workshop. Please note that the LaTeX installation can take a while, since updating and downloading packages can be time-consuming.



## Step 1: Install Homebrew (if not already installed)

First, if you don't have Homebrew installed, open your terminal and enter the following command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

This will install Homebrew, a package manager for macOS, making it easy to install LaTeX and other software.

## Step 2: Install LaTeX via Homebrew

Once Homebrew is installed, you can install LaTeX by running the following command in your terminal:

```bash
brew install --cask mactex-no-gui
```

This command installs the **MacTeX-no-GUI** version, which includes the full LaTeX environment without any graphical applications (such as TeXShop). The download and installation can take a while to start, so be patient—it may seem like nothing is happening initially, but it will eventually begin downloading.

After installation, update LaTeX packages to ensure you have the latest versions. You will need to restart your terminal before running the following commands:

```bash
sudo tlmgr update --self
sudo tlmgr update --all
```

This ensures your LaTeX environment is fully up to date. If you encounter any issues during the installation or update process, check the terminal output for error messages and try to resolve them accordingly. For me it helped to run eval "$(/usr/libexec/path_helper)" and restarting my terminal.

## Step 3: Install VSCode

If you haven't installed Visual Studio Code yet, you can download and install it from the [official VSCode website](https://code.visualstudio.com/).

Once installed, open VSCode and prepare to add the necessary extensions for LaTeX.

## Step 4: Install the LaTeX Workshop Extension

VSCode doesn't natively support LaTeX, so we need to install an extension called **LaTeX Workshop**. This extension provides LaTeX syntax highlighting, compilation, previews, and other useful features.

To install it:
1. Open **VSCode**.
2. Go to the **Extensions** view by clicking on the Extensions icon on the sidebar or pressing `Cmd` + `Shift` + `X`.
3. Search for **LaTeX Workshop**.
4. Click **Install**.

Once installed, LaTeX Workshop will automatically manage compiling your LaTeX files and displaying previews.

### Configuring LaTeX Workshop:
You can customize LaTeX Workshop by going to the settings (open `Cmd` + `,`) and searching for **LaTeX Workshop**. You’ll find options for how you want your documents to compile, preview behavior, and more. For now you can leave the default settings as they are.

## Step 5: Enable Word Wrap in VSCode

LaTeX files can often contain long lines of text, and horizontal scrolling is inconvenient. To make your experience smoother, enable **word wrap** in VSCode so that long lines break automatically within the window.

### To enable word wrap globally:
1. Open VSCode settings (`Cmd` + `,`).
2. Search for **word wrap**.
3. Set **Editor: Word Wrap** to `on`.

Alternatively, you can set word wrap for individual sessions by using the keyboard shortcut `Alt` + `Z`.

Another way to enable word wrap is by using the **Command Palette**:
1. Open the Command Palette by pressing `Cmd` + `Shift` + `P`.
2. Type **Word Wrap** and select **View: Toggle Word Wrap**.

This ensures that lines automatically break without requiring horizontal scrolling.

## Step 6: Compile and preview

Here a quick preview on how it can look when you have setup everything. You can see the LaTeX code on the left and the preview on the right, and by default auto-compilation is enabled. This means that the preview will update automatically when you save the file (or have autosave enabled, something I recommend to have enabled by default on all of your projects). In this case I switched my theme to a light theme, because the dark themed editor was of too much contrast compared to the preview.

![alt text](image.png)


With LaTeX installed via Homebrew and configured in VSCode using the LaTeX Workshop extension, you now have a powerful setup for writing LaTeX documents. The installation may take some time, especially when using the `brew` command, but once it's complete, you’ll have a smooth and customizable LaTeX environment with all the features that VSCode offers, such as Git integration, extensions, and more.
