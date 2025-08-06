import requests
import random
import string
import time

def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_temp_email():
    domain = requests.get("https://api.mail.tm/domains").json()["hydra:member"][0]["domain"]
    username = random_string()
    email = f"{username}@{domain}"
    password = random_string(12)
    
    res = requests.post("https://api.mail.tm/accounts", json={
        "address": email,
        "password": password
    })

    if res.status_code != 201:
        print("Tạo email thất bại:", res.text)
        return None, None, None
    
    token_res = requests.post("https://api.mail.tm/token", json={
        "address": email,
        "password": password
    }).json()

    token = token_res["token"]
    return email, password, token

def create_garena_account(email, password):
    # Đây chỉ là ví dụ. API đăng ký Garena không công khai, cần giả lập HTTP request
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    }

    payload = {
        "email": email,
        "password": password,
        "username": email.split('@')[0],
        "region": "VN"
    }

    print(">>> Đang gửi yêu cầu đăng ký đến Garena...")
    # Giả lập gửi request (không phải API chính thức)
    res = requests.post("https://dummy.garena.api/register", json=payload, headers=headers)

    print(">>> Phản hồi từ Garena (mô phỏng):", res.text)

def wait_for_email(token):
    print(">>> Đang chờ email xác nhận...")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    for i in range(30):
        inbox = requests.get("https://api.mail.tm/messages", headers=headers).json()
        if inbox["hydra:totalItems"] > 0:
            msg_id = inbox["hydra:member"][0]["id"]
            msg = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers).json()
            print(">>> Đã nhận được email:")
            print("Tiêu đề:", msg["subject"])
            print("Nội dung:", msg["text"])
            return
        time.sleep(2)
    print(">>> Không nhận được email xác nhận sau 60s.")

def main():
    email, email_pass, token = create_temp_email()
    if not email:
        return
    garena_pass = random_string(10)

    print("===================================")
    print("Email:", email)
    print("Pass Email:", email_pass)
    print("Pass Garena:", garena_pass)
    print("===================================")

    create_garena_account(email, garena_pass)
    wait_for_email(token)

if __name__ == "__main__":
    main()