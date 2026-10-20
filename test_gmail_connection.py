"""
Diagnostic script to test Gmail SMTP connectivity step-by-step.
"""
import os
import sys
import socket
import smtplib
import time

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = 'smtp.gmail.com'
PORT = 587
EMAIL_USER = 'arvs.bulatao.08@gmail.com'
EMAIL_PASS = 'sbjnjfpzxpceidbt'

print("=" * 60)
print("GMAIL SMTP CONNECTIVITY DIAGNOSTIC")
print("=" * 60)

# Step 1: DNS
print(f"\n[1/6] DNS Resolution for {HOST}...")
try:
    ip = socket.gethostbyname(HOST)
    print(f"  [OK] Resolved to {ip}")
except socket.gaierror as e:
    print(f"  [FAIL] DNS resolution failed: {e}")
    sys.exit(1)

# Step 2: TCP 587
print(f"\n[2/6] TCP connection to {HOST}:{PORT} (5s timeout)...")
start = time.time()
try:
    sock = socket.create_connection((HOST, PORT), timeout=5)
    print(f"  [OK] TCP connected in {time.time()-start:.2f}s")
    sock.close()
    port_587_works = True
except (socket.timeout, OSError) as e:
    print(f"  [FAIL] {e}")
    port_587_works = False

# Step 3: TCP 465
print(f"\n[3/6] TCP connection to {HOST}:465 (SSL fallback, 5s timeout)...")
start = time.time()
try:
    sock = socket.create_connection((HOST, 465), timeout=5)
    print(f"  [OK] TCP connected in {time.time()-start:.2f}s")
    sock.close()
    port_465_works = True
except (socket.timeout, OSError) as e:
    print(f"  [FAIL] {e}")
    port_465_works = False

if not port_587_works and not port_465_works:
    print("\n[FAIL] Both SMTP ports blocked. Check firewall/network.")
    sys.exit(1)

# Step 4: SMTP handshake
server = None
if port_587_works:
    print(f"\n[4/6] SMTP STARTTLS handshake on port 587...")
    start = time.time()
    try:
        server = smtplib.SMTP(HOST, PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        print(f"  [OK] STARTTLS handshake in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        server = None

if server is None and port_465_works:
    print(f"\n[4/6] SMTP SSL handshake on port 465...")
    start = time.time()
    try:
        server = smtplib.SMTP_SSL(HOST, 465, timeout=10)
        server.ehlo()
        print(f"  [OK] SSL handshake in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        server = None

# Step 5: Authentication
if server:
    print(f"\n[5/6] SMTP Authentication as {EMAIL_USER}...")
    try:
        server.login(EMAIL_USER, EMAIL_PASS)
        print(f"  [OK] Authenticated successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"  [FAIL] Authentication FAILED: {e}")
        print("  -> App Password may be invalid. Regenerate at:")
        print("     https://myaccount.google.com/apppasswords")
        try: server.quit()
        except: pass
        sys.exit(1)
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        try: server.quit()
        except: pass
        sys.exit(1)

    # Step 6: Send test email
    print(f"\n[6/6] Sending test email to {EMAIL_USER}...")
    try:
        from email.mime.text import MIMEText
        msg = MIMEText(
            "This is a test email from the Agrostudies system.\n\n"
            "If you received this, your Gmail SMTP configuration is working correctly!\n\n"
            f"Sent at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"From: {EMAIL_USER}\n"
            f"SMTP: {HOST}:{PORT}"
        )
        msg['Subject'] = 'Agrostudies SMTP Test - SUCCESS'
        msg['From'] = f'Agrostudies <{EMAIL_USER}>'
        msg['To'] = EMAIL_USER
        server.sendmail(EMAIL_USER, [EMAIL_USER], msg.as_string())
        print(f"  [OK] Test email SENT to {EMAIL_USER}")
        server.quit()
        email_sent = True
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        try: server.quit()
        except: pass
        email_sent = False
else:
    print(f"\n[5/6] Skipped (no connection)")
    print(f"[6/6] Skipped (no connection)")
    email_sent = False

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if email_sent:
    print("[OK] ALL CHECKS PASSED - Gmail SMTP is working!")
    print(f"  Test email sent to {EMAIL_USER}")
    print("  Check your inbox (and spam folder).")
else:
    print("[FAIL] Email could not be sent. See errors above.")
