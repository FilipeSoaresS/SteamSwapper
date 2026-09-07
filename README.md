# 🎮 Steam Swapper

**Is the economy making games too expensive, and you cannot afford every
game you would like to play?**

Did you know that some people buy accounts that already include specific
games and, in some cases, gain access to those games for much less?

The problem starts when you have several accounts: signing in and out of
Steam, remembering which account has each game, and constantly switching
users can quickly become inconvenient.

That is why **Steam Swapper** was created.

**Steam Swapper** is a lightweight Windows CMD/Batch (`.bat`) utility
designed to make organizing and switching between multiple Steam
accounts easier.

You can register your accounts, assign each one a number, and add a
custom note so you can quickly identify what each account is used for:

``` text
[1] main_account - My main account
[2] games_account - Elden Ring
[3] rpg_account - Baldur's Gate 3
[4] racing_account - Forza Horizon
```

After that, simply enter the desired number and Steam Swapper will
switch to the corresponding account.

**More accounts, less confusion. Pick a number, switch accounts, and
play.**

> **Important:** If you acquire or use third-party accounts, make sure
> you understand the platform's rules and the risks involved. Steam
> Swapper only organizes and simplifies switching between accounts. It
> does not sell, provide, create, or modify Steam accounts.

------------------------------------------------------------------------

## 📁 File Structure

Keep the following files in the same folder:

``` text
Steam Swapper/
│
├── SteamSwapper.bat
├── steam_contas.txt
└── README.md
```

The `steam_contas.txt` file acts as the application's local database.

If it does not exist when Steam Swapper starts, the application creates
an empty file automatically.

------------------------------------------------------------------------

## 🚀 Starting Steam Swapper

Run:

``` text
SteamSwapper.bat
```

The main menu will look similar to this:

``` text
============================================================
                 STEAM ACCOUNT SWAPPER
============================================================

REGISTERED ACCOUNTS:

    [1] main_account - My main account
    [10] games_account - Elden Ring

------------------------------------------------------------

Enter the account NUMBER to launch it.

[N] Register new account
[R] Remove account
[E] Edit note
[X] Exit

------------------------------------------------------------

Choice:
```

From this menu, you can access all Steam Swapper features.

------------------------------------------------------------------------

# ➕ Registering a New Account

From the main menu, press:

``` text
N
```

Registration is completed in three main steps.

## 1. Choose an Account Number

First, choose a number between `0` and `100`.

Example:

``` text
Choose a number between 0 and 100: 15
```

This number becomes the shortcut used to select the account later.

For example:

``` text
[15] games_account - Elden Ring
```

Each number can belong to only one account.

If you try to use a number that is already registered, Steam Swapper
will warn you and ask for another number.

------------------------------------------------------------------------

## 2. Enter the Steam Login

Next, enter the **login name used to sign in to Steam**:

``` text
Steam account login: my_account
```

Use the actual account login, which may be different from the public
profile name displayed on Steam.

------------------------------------------------------------------------

## 3. Add a Note

Steam Swapper will then ask for a note:

``` text
Note:
```

The note helps you remember the purpose of the account or which games
are associated with it.

Examples:

``` text
Main account
```

``` text
Elden Ring
```

``` text
Baldur's Gate 3
```

``` text
Shared games
```

``` text
Forza Horizon 5
```

If no note is entered, the application can use:

``` text
No note
```

------------------------------------------------------------------------

## 4. Confirm the Registration

Steam Swapper displays the information before saving it:

``` text
Number:
    15

Login:
    my_account

Note:
    Elden Ring
```

After confirmation, the account will appear in the main menu:

``` text
[15] my_account - Elden Ring
```

------------------------------------------------------------------------

# 🔄 Switching Accounts

From the main menu, find the account you want to use.

Example:

``` text
[1] main_account - My main account
[10] rpg_account - Baldur's Gate 3
[15] games_account - Elden Ring
```

To select account `15`, type:

``` text
15
```

and press `Enter`.

Steam Swapper will:

1.  Find the Steam login associated with that number.
2.  Close the currently running Steam client.
3.  Wait a few seconds for Steam to shut down.
4.  Launch Steam again using the selected login.

If Steam already remembers the authentication for that account, it may
reuse the existing session.

If Steam requests a password or Steam Guard verification, enter the
information directly in the official Steam client.

> **Steam Swapper does not store your Steam password.**

------------------------------------------------------------------------

# ✏️ Editing an Account Note

From the main menu, press:

``` text
E
```

Steam Swapper will display the registered accounts:

``` text
[1] main_account - My main account
[15] games_account - Elden Ring
[20] rpg_account - RPG
```

Enter the number of the account you want to edit:

``` text
Number: 20
```

The application will show something similar to:

``` text
Account:
    rpg_account

Current note:
    RPG
```

Enter the new note:

``` text
New note: Baldur's Gate 3
```

The account will then appear as:

``` text
[20] rpg_account - Baldur's Gate 3
```

The account number and Steam login remain unchanged. Only the note is
modified.

------------------------------------------------------------------------

# 🗑️ Removing an Account

From the main menu, press:

``` text
R
```

The registered accounts will be displayed:

``` text
[1] main_account - My main account
[5] secondary_account - Old games
[15] games_account - Elden Ring
```

Enter the number you want to remove:

``` text
Number: 5
```

The corresponding entry will be removed from `steam_contas.txt`.

> This only removes the account from **Steam Swapper**. It does not
> delete, disable, or modify the actual Steam account.

------------------------------------------------------------------------

# ↩️ Returning to the Main Menu

On screens where this option is available, enter:

``` text
M
```

to cancel the current operation and return to the main menu.

Example:

``` text
Number: M
```

Steam Swapper will indicate when this option is available:

``` text
M = Return to main menu
```

------------------------------------------------------------------------

# ❌ Exiting Steam Swapper

From the main menu, press:

``` text
X
```

to close Steam Swapper.

------------------------------------------------------------------------

# 💾 How `steam_contas.txt` Works

Steam Swapper uses:

``` text
steam_contas.txt
```

as a simple local database.

Each line follows this format:

``` text
NUMBER|LOGIN|NOTE
```

Example:

``` text
1|main_account|My main account
10|rpg_account|Baldur's Gate 3
15|games_account|Elden Ring
25|racing_account|Forza Horizon 5
```

In this example:

-   `1` is the shortcut number used by Steam Swapper.
-   `main_account` is the Steam login.
-   `My main account` is the note displayed in the menu.

You normally **do not need to edit this file manually**.

Steam Swapper updates it automatically when you register, edit, or
remove an account.

------------------------------------------------------------------------

# 🔐 Passwords and Security

Steam Swapper **does not store Steam passwords**.

The `steam_contas.txt` file contains only:

-   account number;
-   Steam login;
-   custom note.

For example:

``` text
15|my_account|Elden Ring
```

No password is stored in this entry.

If Steam requires authentication, enter your password directly in the
official Steam client.

------------------------------------------------------------------------

# 🛡️ Steam Guard

Steam Guard continues to work normally.

If Steam requests verification when switching accounts, complete the
authentication directly through Steam using the method configured for
that account.

Steam Swapper does not disable, modify, bypass, or interfere with Steam
Guard.

------------------------------------------------------------------------

# 📂 Steam Installation Location

By default, Steam Swapper looks for Steam in:

``` text
C:\Program Files (x86)\Steam\steam.exe
```

or:

``` text
C:\Program Files\Steam\steam.exe
```

If Steam is installed somewhere else, change the `STEAM` variable inside
the `.bat` file.

Example:

``` bat
set "STEAM=D:\Steam\steam.exe"
```

------------------------------------------------------------------------

# 📦 Moving Steam Swapper

You can move Steam Swapper to another folder.

Keep these files together:

``` text
SteamSwapper.bat
steam_contas.txt
README.md
```

For example:

``` text
D:\Apps\Steam Swapper\
```

The application looks for `steam_contas.txt` in the same directory as
the `.bat` file.

------------------------------------------------------------------------

# 💾 Creating a Backup

To back up your registered accounts, copy:

``` text
steam_contas.txt
```

This file contains the account numbers, logins, and notes registered in
Steam Swapper.

To back up the entire application, copy:

``` text
SteamSwapper.bat
steam_contas.txt
README.md
```

------------------------------------------------------------------------

# 🔁 Restoring a Backup

Place your backed-up:

``` text
steam_contas.txt
```

in the same folder as:

``` text
SteamSwapper.bat
```

The registered accounts will appear again the next time Steam Swapper
starts.

------------------------------------------------------------------------

# 🧹 Removing All Registered Accounts

Close Steam Swapper and delete:

``` text
steam_contas.txt
```

The next time the application starts, it will create a new empty file.

This **does not remove any account from Steam**. It only clears Steam
Swapper's local account list.

------------------------------------------------------------------------

# 📝 Complete Usage Example

Suppose you want to organize three accounts.

Register the first account:

``` text
Number: 1
Login: main_account
Note: My main account
```

Then register:

``` text
Number: 10
Login: eldenring123
Note: Elden Ring
```

And:

``` text
Number: 20
Login: forza_user
Note: Forza Horizon 5
```

Your main menu will then look similar to:

``` text
============================================================
                 STEAM ACCOUNT SWAPPER
============================================================

REGISTERED ACCOUNTS:

    [1] main_account - My main account
    [10] eldenring123 - Elden Ring
    [20] forza_user - Forza Horizon 5

------------------------------------------------------------

Enter the account NUMBER to launch it.

[N] Register new account
[R] Remove account
[E] Edit note
[X] Exit

------------------------------------------------------------

Choice:
```

To access the Elden Ring account, enter:

``` text
10
```

To switch to the Forza account, enter:

``` text
20
```

To return to your main account, enter:

``` text
1
```

------------------------------------------------------------------------

# ⌨️ Command Summary

  Command   Function
  --------- ------------------------------------------------
  `0–100`   Launch the account associated with that number
  `N`       Register a new account
  `E`       Edit an account note
  `R`       Remove an account from Steam Swapper
  `M`       Return to the main menu when available
  `X`       Exit Steam Swapper

------------------------------------------------------------------------

# ⚠️ Important Notes

-   Steam Swapper is designed for **Windows**.
-   Steam must be installed.
-   Account shortcut numbers range from `0` to `100`.
-   Each number can be assigned to only one account.
-   Notes are used only for organization.
-   Steam Swapper does not store passwords.
-   Steam Swapper does not bypass Steam Guard.
-   Steam Swapper does not create Steam accounts.
-   Steam Swapper does not buy, sell, or provide Steam accounts.
-   Account switching may depend on how the Steam client manages
    remembered accounts and active sessions.
-   Steam may occasionally request your password or Steam Guard
    verification again.
-   If you use an account that does not belong to you, make sure you
    have permission to access it and understand Steam's applicable
    rules.

------------------------------------------------------------------------

# 🎮 Steam Swapper

Organize your accounts, quickly identify where each game is located, and
simplify switching between Steam users.

``` text
Choose the number → Switch accounts → Play
```
