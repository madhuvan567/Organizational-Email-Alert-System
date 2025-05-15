from imapclient import IMAPClient
import pyzmail
import os
import requests
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMAP_SERVER = "imap.gmail.com"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

print(f"✅ Email agent is running for: {EMAIL}")

def send_telegram_alert(subject, summary, sender):
    message = f"📩 *Delayed Email Alert*\nFrom: {sender}\nSubject: {subject}\nSummary: {summary}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
        response.raise_for_status()
        print(f"🔔 Alert sent for email from {sender} about {subject}")
    except requests.RequestException as e:
        print(f"⚠️ Telegram API error: {e}")

def summarize_text(text):
    try:
        response = model.generate_content(f"Summarize this email:\n{text}")
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Error summarizing text: {e}")
        return text[:200] + "..."

def monitor_email():
    with IMAPClient(IMAP_SERVER) as mail:
        try:
            mail.login(EMAIL, PASSWORD)
            mail.select_folder("INBOX")
        except Exception as e:
            print(f"⚠️ Error logging in: {e}")
            return

        print("🔎 Ignoring existing unseen mails...")
        seen_ids = set(mail.search(['UNSEEN']))
        tracked_emails = {}

        try:
            while True:
                try:
                    print("🔄 Checking for unseen emails...")
                    mail.select_folder("INBOX")
                    unseen_now = mail.search(['UNSEEN'])
                    new_ids = [eid for eid in unseen_now if eid not in seen_ids and eid not in tracked_emails]

                    print(f"Found {len(new_ids)} new unseen emails.")

                    for eid in new_ids:
                        # Fetch email body without marking as read
                        response = mail.fetch([eid], ['BODY.PEEK[]'])
                        if eid not in response or b'BODY[]' not in response[eid]:
                            print(f"⚠️ Failed to fetch email {eid}. Response keys: {response.get(eid, {}).keys()}")
                            continue

                        raw_email = response[eid][b'BODY[]']  
                        try:
                            message = pyzmail.PyzMessage.factory(raw_email)
                            print(f"✅ Successfully fetched email {eid}")
                        except Exception as e:
                            print(f"⚠️ Error parsing email {eid}: {e}")
                            continue

                        sender = message.get_address('from')[1]
                        subject = message.get_subject() or "(No Subject)"
                        body = ""

                        # Safely extract email body
                        if message.text_part:
                            charset = message.text_part.charset or 'utf-8'
                            try:
                                body = message.text_part.get_payload().decode(charset, errors='replace')
                            except Exception as e:
                                print(f"⚠️ Error decoding text part for email {eid}: {e}")
                                body = "(Failed to decode text part)"
                        elif message.html_part:
                            charset = message.html_part.charset or 'utf-8'
                            try:
                                body = message.html_part.get_payload().decode(charset, errors='replace')
                            except Exception as e:
                                print(f"⚠️ Error decoding HTML part for email {eid}: {e}")
                                body = "(Failed to decode HTML part)"

                        print(f"📧 Tracking new email: {subject} from {sender}")

                        if '''enter your organization emai endpoit(i.e. @acropoli.in)''' in sender:
                            tracked_emails[eid] = {
                                "timestamp": time.time(),
                                "subject": subject,
                                "sender": sender,
                                "body": body
                            }

                    # Check for delayed emails
                    for eid in list(tracked_emails.keys()):
                        record = tracked_emails[eid]
                        if time.time() - record["timestamp"] > 45:
                            print(f"⏰ Email {eid} is older than 45 seconds, checking if seen...")
                            flags = mail.get_flags([eid])
                            print(f"Flags for email {eid}: {flags}")

                            if b'\\Seen' not in flags.get(eid, []):
                                print(f"⚠️ Email {eid} has not been seen, sending alert.")
                                summary = summarize_text(record["body"])
                                send_telegram_alert(record["subject"], summary, record["sender"])
                            else:
                                print(f"✅ Email {eid} has been marked as seen.")

                            seen_ids.add(eid)
                            del tracked_emails[eid]

                    time.sleep(10)

                except Exception as e:
                    print(f"⚠️ Error during email monitoring: {e}")
                    time.sleep(5)

        except KeyboardInterrupt:
            print("🛑 Script stopped by user.")
            return  

# ==== ENTRY POINT ====
if __name__ == "__main__":
    print("📬 Monitoring new emails with 30-second delayed alert...")
    monitor_email()