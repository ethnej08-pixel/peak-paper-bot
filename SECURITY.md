# Dashboard security

The dashboard is a local-only HTTP server bound to `127.0.0.1:8790`. It now requires HTTP Basic authentication before serving account and trade data.

## Start the dashboard on macOS

From the repository directory, generate a strong one-time password and start the app in the same Terminal session:

```sh
export PEAK_DASHBOARD_USER=peak
export PEAK_DASHBOARD_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
printf 'Dashboard username: %s\nDashboard password: %s\n' "$PEAK_DASHBOARD_USER" "$PEAK_DASHBOARD_PASSWORD"
python3 bot.py
```

Save the printed password in a password manager. Open [http://127.0.0.1:8790](http://127.0.0.1:8790) and enter the username and password when the browser prompts. Keep that Terminal session running; stopping it ends the dashboard and its environment variables. Generate a new password when starting a new session.

You can choose a password yourself instead, but it must be at least 16 characters. Do not put it in source code, commit it, or paste it into chat.

## Security notes

- The server refuses to start in dashboard mode if the password is missing or shorter than 16 characters.
- Credentials are read from environment variables and are not written to `state.json` or Git.
- Failed or missing credentials receive HTTP 401; the response is not cached.
- The server remains bound to loopback (`127.0.0.1`), not all network interfaces.
- HTTP Basic authentication does not encrypt traffic. Do not expose this HTTP server directly to the internet or a shared network. If remote access is needed, put it behind a properly configured HTTPS reverse proxy or a VPN and revisit the authentication design.
- The GitHub Actions `--cloud` and `--check` paths do not start the dashboard and do not require this dashboard password.
- This protects the dashboard endpoint; it does not turn the paper-trading bot into a broker-connected app or add real trading capabilities.
