# NWGS Grid - Domain, email and sign-in

How the custom domain, the sending mailbox and the sign-in redirects are wired,
and how to change any of them again.

> Hand-maintained. Unlike the five generated references, `scripts/build_docs.py`
> does not write this file, so edits here survive a documentation rebuild.
> Update it whenever the domain, the mailbox or the Supabase URLs change.

**Current configuration**

| Setting | Value |
|---|---|
| Public address | `https://nwgsgrid.com` |
| Registrar and DNS host | IONOS |
| Hosting | GitHub Pages, published by Actions from `site_src/template.html` |
| `www` host | No DNS record. The apex is the only published name. |
| Contact address, Reply-To and sending mailbox | `alerts@nwgsgrid.com` (one mailbox for all three) |
| Sending mailbox for sign-in links and alert emails | `alerts@nwgsgrid.com` at IONOS |
| Accounts, sign-in and alert rules | Supabase |

---

## 1. How the domain reaches the site

Three things have to agree. If any one of them is wrong the site either fails
its DNS check or quietly reverts to the `github.io` address.

1. **The DNS zone at IONOS** publishes four `A` records on the apex pointing at
   GitHub Pages.
2. **`site_src/CNAME`** contains `nwgsgrid.com`, and `scripts/build_site.py`
   copies that file into the published output on every build.
3. **Settings, Pages, Custom domain** in the repository is set to
   `nwgsgrid.com`.

Point 2 is the one that is easy to miss. GitHub Pages reads the custom domain
from a `CNAME` file **inside what was deployed**, not from the repository and
not from the settings page alone. When a site is published by Actions rather
than from a branch, a build that does not copy `CNAME` into its output clears
the custom domain the next time it runs, and nothing reports an error. The
build prints `Custom domain: nwgsgrid.com` when the file was found; if that
line is missing from the build log, the domain is about to be lost.

### The DNS records

Four apex records, and nothing on `www`:

```
A   @   185.199.108.153
A   @   185.199.109.153
A   @   185.199.110.153
A   @   185.199.111.153
```

Leave every `MX`, `TXT` and other mail record exactly as it is. They carry the
mailbox and have nothing to do with the website.

### Setting it up from scratch

1. In IONOS, open **Domains & SSL**, the domain, then **DNS**.
2. Add the four `A` records above, one at a time. **Before saving each one,
   switch off "Add DNS record for www".** Leaving it on is what makes this
   fiddly: see the traps below.
3. Set TTL to the shortest IONOS offers, 1 minute, while setting up. Raise it
   later once everything resolves.
4. Confirm the zone is serving them, asking the nameserver directly rather
   than a cache:

   ```powershell
   nslookup -type=A nwgsgrid.com ns1098.ui-dns.com
   ```

   All four addresses should be listed. A local or public resolver can be
   minutes to an hour behind, so this authoritative query is the one that
   tells the truth.

5. Confirm nothing is published on `www`:

   ```powershell
   nslookup -type=A www.nwgsgrid.com ns1098.ui-dns.com
   ```

   `Non-existent domain` is the wanted answer.

6. In the repository, **Settings, Pages**. Clear the Custom domain box, press
   **Save**, type `nwgsgrid.com`, press **Save** again. Clearing first forces a
   fresh check rather than reusing the last result.
7. Wait for the green **DNS check successful**, then tick **Enforce HTTPS**.
   The certificate is issued after the check passes, and the tick box stays
   greyed out until it is ready. Fifteen minutes to an hour is normal.
8. Confirm the live site answers over HTTPS:

   ```powershell
   curl.exe -I https://nwgsgrid.com
   ```

   `HTTP/1.1 200 OK` with `Server: GitHub.com`. Use `curl.exe`, not `curl`:
   in PowerShell, `curl` is an alias for `Invoke-WebRequest`, which does not
   accept `-I` and fails with "A drive with the name 'https' does not exist".

### Traps, all of which were hit once

**IONOS creates a matching `www` record whenever an apex record is added.**
The dialog carries an **Add DNS record for www** switch that defaults to on,
and the preview shows a second line for `www`. Because a host cannot hold both
a `CNAME` and an `A` record, adding the apex records with that switch on
removes an existing `www` `CNAME`. This can repeat indefinitely: add the apex
records, the `www` `CNAME` disappears, re-create the `CNAME`, the apex records
are disabled instead. Switch it off and the problem goes away.

**IONOS disables rather than deletes conflicting records.** A record the panel
shows as removed can still be published by the zone, and a disabled record can
come back when the record that displaced it is deleted. Trust the
authoritative `nslookup`, never the panel.

**Deleting the `www` records can take the apex with them.** Select by host.
Deleting everything of type `A` at once leaves the site with no address at all,
and GitHub then reports `NotServedByPagesError` for a configuration that was
correct an hour earlier.

**GitHub caches a failed lookup for up to an hour.** After the zone is fixed,
Settings, Pages can keep showing `NotServedByPagesError` for a while. There is
no way to force a refresh. Wait, then clear and re-save the domain. A `301`
from `https://<user>.github.io/<repo>/` to `https://nwgsgrid.com/` means
GitHub has already accepted the domain and only the check is behind.

**A local resolver can serve a stale empty answer all evening.** `ipconfig
/flushdns` clears the Windows cache; a home router's cache is separate and
usually cannot be cleared. Query the authoritative nameserver when in doubt.

### Changing to a different domain

1. Edit `site_src/CNAME` to hold the new name, nothing else, no scheme and no
   trailing slash.
2. Point the new domain's DNS at the same four addresses.
3. Update **Settings, Pages**.
4. Update `SITE` in `scripts/send_alerts.py`, `url` in `CITATION.cff`, the live
   link in `README.md`, and the Supabase URLs in section 3 below.
5. Run the workflow and check the build log prints the new domain.

---

## 2. The sending mailbox

Two different systems send mail, and both should come from the same address so
that neither looks like a stranger in the inbox.

| Mail | Sent by | Credentials live in |
|---|---|---|
| Sign-in link ("magic link") | Supabase | Supabase, Authentication, Emails, SMTP Settings |
| Weekly alert email | `scripts/send_alerts.py` in the workflow | GitHub repository secrets |

### Creating the mailbox

In IONOS, open **Email**, create the mailbox on the domain, and set a password. One mailbox does both jobs: `alerts@nwgsgrid.com` sends the sign-in links and the weekly alerts, and receives replies, because it is also the Reply-To and the contact address published on the site, in LICENSE and in CITATION.cff. Anyone answering an alert reaches that mailbox, so it has to be read, not left as a send-only address.

### Pointing Supabase at it

Authentication, Emails, **SMTP Settings**. Turn on **Enable custom SMTP** and
fill in:

```
Sender email address   alerts@nwgsgrid.com
Sender name            NWGS Grid
Host                   smtp.ionos.com
Port number            465
Username               alerts@nwgsgrid.com
Password               the mailbox password
```

Confirm the host and port against IONOS's own mail-settings page, since both
vary by region and package. If 465 is refused, try 587.

Two reasons this is not optional. Supabase's built-in email service is rate
limited to a few messages an hour and is meant for development, so on a public
site the fourth person to request a sign-in link within an hour silently
receives nothing. And **Sender name** is what decides the name in the
recipient's inbox: left unset, sign-in emails arrive under whatever name the
underlying account carries, which on a personal mailbox is a personal name.

### Pointing the alert emails at it

Settings, Secrets and variables, Actions:

| Secret | Value |
|---|---|
| `SMTP_USER` | `alerts@nwgsgrid.com` |
| `SMTP_PASSWORD` | the mailbox password |
| `SMTP_HOST` | `smtp.ionos.com` |

`send_alerts.py` reads `SMTP_HOST` with a default, so adding that secret is all
that is needed to move provider. `SMTP_PORT` defaults to 465 and only needs
setting if the provider wants another port.

The script sets `From: NWGS Grid alerts <SMTP_USER>` and a separate `Reply-To`,
so replies reach a person while the sender stays institutional. Both the plain
text and HTML footers carry the contact address.

### Changing the contact address across the project

The address appears in six places. Change all six together, or citations and
emails disagree with the site:

| File | What it is |
|---|---|
| `site_src/template.html` | `const EMAIL`, used by every contact and license link |
| `scripts/send_alerts.py` | `Reply-To` and the two email footers |
| `README.md` | Contact line |
| `LICENSE` | Permission-request address |
| `CITATION.cff` | Author email in the citation record |
| `.github/workflows/weekly-update.yml` | Contact line in the release notes |

In the template the address is assembled from two pieces at run time rather
than written out, which keeps it out of the simplest address scrapers. Keep
that shape when changing it:

```javascript
const EMAIL = ['alerts','nwgsgrid.com'].join('@');
```

Then check nothing was missed:

```powershell
git grep -n "old-address@example.com"
```

---

## 3. Supabase sign-in and redirects

Authentication, **URL Configuration**:

| Field | Value |
|---|---|
| Site URL | `https://nwgsgrid.com` |
| Redirect URLs | `https://nwgsgrid.com/**` |

**Site URL** is the fallback a sign-in link returns to. **Redirect URLs** is an
allow list: a redirect the site asks for that is not on the list is ignored,
and the link falls back to Site URL instead. The site asks to return to
whatever address it is being served from, so both have to name the live domain.

This is the cause of the "localhost refused to connect" that a new account sees
after clicking a sign-in link: Site URL was still at its default of
`http://localhost:3000`, so every link in every email pointed at the
recipient's own machine. The symptom appears in the recipient's browser, not in
any log, and the request never reaches the project.

Keep an entry for any other address the site is served from, including the
`github.io` address if it is still reachable, so sign-in works there too while
a domain change settles.

### Testing it end to end

1. Open `https://nwgsgrid.com/#myalerts` in a browser with no session.
2. Request a link with a real mailbox.
3. Check the sender shows as **NWGS Grid**, not a personal name.
4. Click the link. It must land back on `nwgsgrid.com`, signed in.
5. Add an alert, confirm it appears, then delete it.

If the link lands on localhost, the redirect configuration above is wrong. If
no mail arrives, custom SMTP is off or its credentials are wrong; Supabase
shows delivery failures under Authentication, Logs.

### What is safe to publish

`site_src/supabase.json` holds the project URL and the **publishable** key, and
both are meant to be public: every row is protected by row-level security, so a
visitor holding that key can still only read and write their own rows.

The **secret** key is different and must never appear in the site, the
template, a committed file or a log. It exists only as the `SUPABASE_SECRET_KEY`
repository secret, read by `send_alerts.py` inside the workflow, because
sending the weekly email means reading every subscriber's rules and that
deliberately bypasses row-level security.

---

## 4. After any change here

```powershell
nslookup -type=A nwgsgrid.com ns1098.ui-dns.com   # four addresses
curl.exe -I https://nwgsgrid.com                  # 200, Server: GitHub.com
```

Then run the workflow once and confirm the build log contains:

```
Custom domain: nwgsgrid.com
```

and that a sign-in link arrives from the right name and returns to the right
address.
