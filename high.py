import requests, random, string, time
from bs4 import BeautifulSoup

def random_str(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def create_temp_email():
    r1 = requests.get("https://api.mail.tm/domains")
    domain = r1.json()["hydra:member"][0]["domain"]
    user = random_str(10)
    email = f"{user}@{domain}"
    passwd = random_str(12)
    acc = requests.post("https://api.mail.tm/accounts", json={"address":email,"password":passwd})
    acc.raise_for_status()
    tok = requests.post("https://api.mail.tm/token", json={"address":email,"password":passwd})
    tok.raise_for_status()
    return email, passwd, tok.json()["token"]

def register_garena(email, garena_pass):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
    })
    # 1. Truy cập trang để lấy cookie và CSRF token
    r = session.get("https://sso.garena.com/universal/register?locale=en")
    soup = BeautifulSoup(r.text, "html.parser")
    token_input = soup.select_one("input[name=csrf_token]")
    csrf = token_input["value"] if token_input else None

    payload = {
        "email": email,
        "password": garena_pass,
        "username": email.split("@")[0],
        "csrf_token": csrf,
        # thêm các trường region, timezone nếu bắt buộc
    }

    post = session.post("https://sso.garena.com/universal/register?locale=en", data=payload)
    return post.status_code, post.text

def wait_email(token):
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(30):
        inbox = requests.get("https://api.mail.tm/messages", headers=headers).json()
        if inbox.get("hydra:totalItems",0) > 0:
            msg = requests.get(f"https://api.mail.tm/messages/{inbox['hydra:member'][0]['id']}", headers=headers).json()
            return msg.get("text") or msg.get("html")
        time.sleep(2)
    return None

def main():
    email, email_pass, token = create_temp_email()
    garena_pass = random_str(10)
    print("Email:", email, "Email pass:", email_pass)
    print("Garena pass:", garena_pass)
    status, resp = register_garena(email, garena_pass)
    print("Status:", status)
    if "captcha" in resp.lower():
        print("⚠️ Có khả năng hệ thống yêu cầu CAPTCHA.")
    print("Đang chờ email xác nhận...")
    content = wait_email(token)
    if content:
        print("Email xác nhận đến, nội dung:", content)
    else:
        print("Không nhận được email.")

if __name__=="__main__":
    main()