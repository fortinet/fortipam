# SSMS-v20 — Microsoft SQL Server Management Studio 20 Launcher

Custom launcher for **Microsoft SQL Server Management Studio v20** (SSMS) using **FortiClient PAM** script-based credential injection.

## Description

This launcher starts SSMS 20 on the target machine and automatically fills the **"Connect to Server"** dialog:

1. Clears and fills the **Server name** field with `$HOST`
2. Selects **SQL Server Authentication** as the authentication method
3. Clears and fills the **Login** field with `$USER`
4. Fills the **Password** field with `$PASSWORD`
5. Sets the encryption option to **Optional**
6. Clicks **Connect**

Credentials are injected by FortiClient PAM via `fct-script` commands — the user never sees the password.

## Requirements

- **FortiClient PAM 7.4.4 or later** (minimum version) installed on the client machine (this launcher relies on FortiClient PAM `fct-script` automation)
- SSMS 20 installed at the default path:
  `C:\Program Files (x86)\Microsoft SQL Server Management Studio 20\Common7\IDE\Ssms.exe`
  (adjust the `exe` path in the config if installed elsewhere)
- Target SQL Server configured for **SQL Server Authentication**

## Notes

- Launcher type: `other`, no privilege elevation, 15 s launch timeout
- The window-path selectors (`WindowsForms10.Window.8.app.0..*`) match the SSMS 20 "Connect to Server" dialog; other SSMS versions may use different control paths
- The **Encryption** dropdown is set to `Optional`; change step 7 of the script if your environment enforces strict encryption