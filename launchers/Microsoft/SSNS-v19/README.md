# SSMS-v19 — Microsoft SQL Server Management Studio 19 Launcher

Custom launcher for **Microsoft SQL Server Management Studio v19** (SSMS) using **FortiClient PAM** script-based credential injection.

## Description

This launcher starts SSMS 19 on the target machine and automatically fills the **"Connect to Server"** dialog:

1. Clears and fills the **Server name** field with `$HOST`
2. Selects **SQL Server Authentication** as the authentication method
3. Clears and fills the **Login** field with `$USER`
4. Fills the **Password** field with `$PASSWORD`
5. Clicks **Connect**

Credentials are injected by FortiClient PAM via `fct-script` commands — the user never sees the password.

## Requirements

- **FortiClient PAM 7.4.4 or later** (minimum version) installed on the client machine (this launcher relies on FortiClient PAM `fct-script` automation)
- FPAM 1.7 or later version  
- SSMS 19 should be add in `SYSTEM` PATH variable or addjust executable path accordingly  
- Target SQL Server configured for **SQL Server Authentication**  

## Notes

- Launcher type: `other`, no privilege elevation, 15 s launch timeout
- The window-path selectors (`WindowsForms10.Window.8.app.0..*`) match the SSMS 19 "Connect to Server" dialog; other SSMS versions may use different control paths
- The **Encryption** connection is not enabled in this launcher