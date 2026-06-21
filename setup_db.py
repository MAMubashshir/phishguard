"""
setup_db.py
Initialises the SQLite database for PhishGuard with all required tables
and loads sample data (education modules, quiz questions, phishing
simulation scenarios, and a default admin account).

Run this once before starting the app:
    python setup_db.py
"""

import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "phishguard.db"


def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            FOREIGN KEY (module_id) REFERENCES modules(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (module_id) REFERENCES modules(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            is_phishing INTEGER NOT NULL,
            explanation TEXT NOT NULL,
            difficulty TEXT NOT NULL DEFAULT 'easy'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS simulation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            simulation_id INTEGER NOT NULL,
            user_answer INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (simulation_id) REFERENCES simulations(id)
        )
    """)

    conn.commit()


def seed_admin(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE role = 'admin'")
    if cur.fetchone():
        return  # admin already exists

    cur.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (
            "admin",
            "admin@phishguard.com",
            generate_password_hash("Admin@1234"),
            "admin",
        ),
    )
    conn.commit()
    print("Default admin created -> email: admin@phishguard.com | password: Admin@1234")


def seed_modules(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM modules")
    if cur.fetchone()[0] > 0:
        return  # already seeded

    modules = [
        (
            "Introduction to Phishing",
            "Fundamentals",
            "Phishing is a type of social engineering attack where criminals impersonate "
            "trusted organisations or individuals to trick victims into revealing sensitive "
            "information such as passwords, credit card numbers, or personal data. Phishing "
            "attacks can arrive via email, text message, phone call, or fake websites. "
            "Understanding what phishing looks like is the first step in protecting yourself."
        ),
        (
            "Email Phishing Techniques",
            "Techniques",
            "Email phishing is the most common form of phishing. Attackers send emails that "
            "appear to come from legitimate companies (banks, delivery services, employers) "
            "and ask the recipient to click a link, open an attachment, or provide login "
            "details. Common red flags include urgent language, spelling mistakes, mismatched "
            "sender addresses, and suspicious links that don't match the real company domain."
        ),
        (
            "Spear Phishing and Targeted Attacks",
            "Techniques",
            "Spear phishing is a highly targeted form of phishing where attackers research a "
            "specific individual or organisation before crafting a personalised message. These "
            "attacks often reference real names, job titles, or recent events to appear more "
            "convincing. Business Email Compromise (BEC), where attackers impersonate a CEO or "
            "manager, is a common form of spear phishing used to trick employees into "
            "transferring money or sensitive data."
        ),
        (
            "Smishing and Vishing",
            "Techniques",
            "Smishing (SMS phishing) uses text messages to trick victims, often claiming to be "
            "from a delivery company or bank, asking them to click a link. Vishing (voice "
            "phishing) uses phone calls, where attackers impersonate tech support, government "
            "agencies, or banks to extract sensitive information verbally. Both rely on "
            "creating a sense of urgency or fear to bypass careful thinking."
        ),
        (
            "How to Protect Yourself",
            "Prevention",
            "To protect against phishing: always verify the sender's email address carefully, "
            "never click links in unsolicited messages, hover over links to check the real "
            "destination before clicking, enable multi-factor authentication (MFA) wherever "
            "possible, keep software updated, and report suspicious messages to your IT "
            "department or email provider rather than responding to them directly."
        ),
    ]
    cur.executemany(
        "INSERT INTO modules (title, category, content) VALUES (?, ?, ?)", modules
    )
    conn.commit()


def seed_quiz_questions(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM quiz_questions")
    if cur.fetchone()[0] > 0:
        return

    # (module_id, question, a, b, c, d, correct_letter)
    questions = [
        (1, "What is phishing?", "A type of computer virus", "A social engineering attack to steal information", "A method of encrypting data", "A type of firewall", "B"),
        (1, "Phishing attacks can arrive via:", "Email only", "Phone calls only", "Email, SMS, and phone calls", "Only fax machines", "C"),
        (1, "What is the main goal of a phishing attack?", "To slow down your computer", "To steal sensitive information", "To improve email security", "To update software", "B"),
        (1, "Which of these is a common phishing target?", "Login credentials", "Credit card numbers", "Personal identification details", "All of the above", "D"),
        (1, "True or False: Phishing only targets large companies.", "True", "False", "Only true on weekends", "Only true for banks", "B"),

        (2, "Which of these is a common red flag in phishing emails?", "Correct grammar", "Urgent language demanding immediate action", "A familiar logo", "A short email", "B"),
        (2, "What should you check before clicking a link in an email?", "The email's font", "The real destination URL by hovering over it", "The time it was sent", "The email's signature only", "B"),
        (2, "A mismatched sender address is a sign of:", "A legitimate email", "A potential phishing email", "A spam filter working correctly", "A secure email", "B"),
        (2, "What is the safest action with a suspicious email attachment?", "Open it to check", "Forward it to friends", "Do not open it and report it", "Reply asking for more details", "C"),
        (2, "Email phishing most commonly impersonates:", "Random strangers", "Banks, delivery services, and employers", "Search engines only", "Operating systems only", "B"),

        (3, "What is spear phishing?", "A generic mass phishing email", "A highly targeted phishing attack using personal information", "A type of virus", "A firewall setting", "B"),
        (3, "What is Business Email Compromise (BEC)?", "A virus that compromises a business website", "Attackers impersonating executives to trick employees", "A type of firewall breach", "A spam filter", "B"),
        (3, "Spear phishing attacks often use:", "Random email addresses", "Real names, job titles, or recent events", "Only fake phone numbers", "Encrypted attachments only", "B"),
        (3, "Why is spear phishing more dangerous than generic phishing?", "It's slower", "It's more personalised and convincing", "It only targets computers, not humans", "It cannot be reported", "B"),
        (3, "A common BEC scenario involves:", "Updating antivirus software", "A fake CEO requesting an urgent money transfer", "Resetting a Wi-Fi password", "Installing a printer driver", "B"),

        (4, "What is smishing?", "Phishing via voice calls", "Phishing via SMS text messages", "Phishing via fax", "Phishing via social media only", "B"),
        (4, "What is vishing?", "Phishing via SMS", "Phishing via voice/phone calls", "Phishing via email", "Phishing via QR codes", "B"),
        (4, "Smishing messages often claim to be from:", "Delivery companies or banks", "Local libraries", "School teachers", "Weather services", "A"),
        (4, "What tactic do vishing callers commonly use?", "Offering long-term discounts", "Creating urgency or fear", "Sending detailed invoices", "Scheduling future calls only", "B"),
        (4, "If you receive a suspicious text asking for personal details, you should:", "Reply immediately", "Click the link to verify", "Ignore or report it, do not click links", "Forward it to all contacts", "C"),

        (5, "What is the best way to verify a suspicious email?", "Reply to the sender directly", "Contact the company through official channels", "Click the link to see where it goes", "Forward it to coworkers", "B"),
        (5, "What does MFA stand for?", "Multiple File Access", "Multi-Factor Authentication", "Mobile First Application", "Managed Firewall Access", "B"),
        (5, "Why is MFA effective against phishing?", "It blocks all emails", "It adds an extra verification step beyond just a password", "It deletes phishing emails automatically", "It slows down the internet", "B"),
        (5, "What should you do if you suspect you clicked a phishing link?", "Ignore it and continue browsing", "Change your passwords and report it to IT/security", "Restart your computer only", "Wait and see what happens", "B"),
        (5, "Keeping software updated helps protect against phishing because:", "It changes your wallpaper", "It patches security vulnerabilities attackers might exploit", "It makes your computer faster only", "It is unrelated to phishing", "B"),
    ]
    cur.executemany(
        """INSERT INTO quiz_questions
           (module_id, question, option_a, option_b, option_c, option_d, correct_option)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        questions,
    )
    conn.commit()


def seed_simulations(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM simulations")
    if cur.fetchone()[0] > 0:
        return

    # (title, sender, subject, body, is_phishing, explanation, difficulty)
    simulations = [
        (
            "Bank Account Verification",
            "security@yourbank-support.com",
            "URGENT: Verify Your Account Now or It Will Be Suspended",
            "Dear Customer, we have detected unusual activity on your account. "
            "Click the link below within 24 hours to verify your identity or your "
            "account will be permanently suspended. http://yourbank-secure-verify.com",
            1,
            "This is phishing. Red flags: urgent threatening language, a suspicious "
            "sender domain that mimics but is not the real bank domain, and a generic "
            "greeting ('Dear Customer') instead of your actual name.",
            "easy",
        ),
        (
            "Monthly Newsletter",
            "newsletter@nationalgeographic.com",
            "Your June Newsletter: Exploring the Amazon Rainforest",
            "Hi there, check out this month's stories on wildlife conservation and "
            "our upcoming documentary releases. Read more on our official website.",
            0,
            "This is legitimate. The sender domain matches the real organisation, "
            "there is no urgent call to action, and no request for personal information.",
            "easy",
        ),
        (
            "Package Delivery Failed",
            "delivery@dhI-shipping-status.com",
            "Delivery Failed - Action Required",
            "We attempted to deliver your package but failed. Please confirm your "
            "address and pay a small redelivery fee here: http://dhI-redelivery.net",
            1,
            "This is phishing. Red flags: a misspelled domain (dhI instead of DHL), "
            "a request for payment to 'redeliver' a package, and pressure to act "
            "quickly without verifying through official channels.",
            "medium",
        ),
        (
            "IT Department Password Reset",
            "it-support@company-internal.net",
            "Your Password Will Expire in 24 Hours",
            "Your network password will expire soon. Click here to reset it "
            "immediately and avoid being locked out of your account: "
            "http://company-internal-resetportal.com/reset",
            1,
            "This is phishing. Red flags: external domain pretending to be an internal "
            "IT department, urgency to act within 24 hours, and a link that does not "
            "match the organisation's real domain.",
            "medium",
        ),
        (
            "Team Meeting Reminder",
            "calendar@yourcompany.com",
            "Reminder: Weekly Team Sync at 10:00 AM",
            "This is a reminder of our weekly team meeting today at 10:00 AM in "
            "Conference Room B. Please review the attached agenda before joining.",
            0,
            "This is legitimate. It matches the company's real domain, contains no "
            "urgent threats, and does not request sensitive information.",
            "easy",
        ),
        (
            "Tax Refund Notification",
            "refunds@gov-taxservice-online.com",
            "You Are Eligible for a Tax Refund of $850",
            "Our records show you are eligible for a refund. To claim your refund, "
            "please provide your bank account and social security number using the "
            "secure form here: http://gov-taxservice-online.com/claim",
            1,
            "This is phishing. Government agencies do not request bank details or "
            "social security numbers via email. The domain is not an official "
            "government (.gov) domain.",
            "medium",
        ),
        (
            "CEO Urgent Wire Transfer Request",
            "ceo.office@compnay-hq.com",
            "Urgent: Need You to Process a Payment Today",
            "I'm in a meeting and can't talk, but I need you to urgently wire $15,000 "
            "to a new vendor account. Please action this immediately and confirm once done.",
            1,
            "This is phishing (Business Email Compromise). Red flags: misspelled domain "
            "('compnay' instead of 'company'), urgency, unusual request bypassing normal "
            "payment procedures, and unavailability to verify by phone.",
            "hard",
        ),
        (
            "Software Subscription Receipt",
            "billing@adobe.com",
            "Your Receipt for Creative Cloud Subscription",
            "Thank you for your payment of $20.99 for your monthly Creative Cloud "
            "subscription. View your invoice in your account dashboard at adobe.com.",
            0,
            "This is legitimate. The domain matches the real company, the amount is "
            "reasonable, and it directs you to log in directly via the official website "
            "rather than an embedded link.",
            "easy",
        ),
        (
            "Social Media Security Alert",
            "security@faceb00k-alerts.com",
            "Someone Tried to Log Into Your Account",
            "We noticed a login attempt from an unrecognised device. If this wasn't you, "
            "secure your account immediately by confirming your password here: "
            "http://faceb00k-alerts.com/secure",
            1,
            "This is phishing. Red flags: the domain uses numbers to mimic letters "
            "('faceb00k' instead of 'facebook'), and it asks you to 'confirm your "
            "password' through an external link rather than the real platform.",
            "hard",
        ),
        (
            "University Library Notice",
            "library@youruniversity.edu",
            "Reminder: Book Return Due in 3 Days",
            "This is a reminder that your borrowed book 'Introduction to Networking' "
            "is due for return in 3 days. Visit the library portal to renew if needed.",
            0,
            "This is legitimate. It comes from an official .edu domain, contains routine "
            "information, and does not request sensitive personal or financial details.",
            "easy",
        ),
    ]
    cur.executemany(
        """INSERT INTO simulations
           (title, sender, subject, body, is_phishing, explanation, difficulty)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        simulations,
    )
    conn.commit()


def main():
    conn = sqlite3.connect(DB_NAME)
    create_tables(conn)
    seed_admin(conn)
    seed_modules(conn)
    seed_quiz_questions(conn)
    seed_simulations(conn)
    conn.close()
    print(f"Database '{DB_NAME}' set up successfully with sample data.")


if __name__ == "__main__":
    main()
