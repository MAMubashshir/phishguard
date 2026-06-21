# PhishGuard — Manual Test Case Documentation

This document records the manual test cases executed against the PhishGuard
application, matching Section 5 (Testing) of the Final Technical Report.

| Test ID | Feature | Test Description | Expected Result | Actual Result | Pass/Fail |
|---------|---------|-------------------|------------------|----------------|-----------|
| TC-01 | Registration | Register with valid details | Account created, redirected to login | As expected | ✅ Pass |
| TC-02 | Registration | Register with duplicate email | Error message displayed | As expected | ✅ Pass |
| TC-03 | Login | Login with correct credentials | User logged in, redirected to dashboard | As expected | ✅ Pass |
| TC-04 | Login | Login with wrong password | "Invalid email or password" shown | As expected | ✅ Pass |
| TC-05 | Education Module | View a learning module | Module content displayed correctly | As expected | ✅ Pass |
| TC-06 | Quiz | Complete a quiz with all correct answers | Score 5/5 displayed | As expected | ✅ Pass |
| TC-07 | Quiz | Submit quiz with no answers selected | Browser validation blocks submission (required fields) | As expected | ✅ Pass |
| TC-08 | Simulation | Correctly identify phishing scenario | "Correct!" message shown, result saved | As expected | ✅ Pass |
| TC-09 | Simulation | Incorrectly identify scenario | Corrective explanation shown, result saved | As expected | ✅ Pass |
| TC-10 | Dashboard | View progress after completing activities | Updated scores and progress % shown | As expected | ✅ Pass |
| TC-11 | Admin Panel | Access admin panel as regular user | Redirected to dashboard, "Access denied" message | As expected | ✅ Pass |
| TC-12 | Admin Panel | Access admin panel as admin user | Full user performance table displayed | As expected | ✅ Pass |
| TC-13 | Security | SQL injection attempt in login email field | Input treated as plain text, login rejected safely | As expected | ✅ Pass |
| TC-14 | Security | Access protected page without logging in | Redirected to login page with warning message | As expected | ✅ Pass |

## How These Tests Were Run

Tests were executed using a combination of:
1. Manual browser testing (Chrome and Firefox)
2. Automated `curl` requests to verify HTTP status codes and response content during development

## Notes

- All passwords are hashed using Werkzeug's `generate_password_hash` (bcrypt-based) — verified by inspecting the `users` table directly; no plain-text passwords are stored.
- All database queries use parameterised statements (`?` placeholders), preventing SQL injection.
- Session-based authentication correctly blocks access to `/dashboard`, `/admin`, `/quiz/<id>`, and `/simulation` routes for unauthenticated users.
