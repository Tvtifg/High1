import asyncio
import random
import string
import time
import requests
import json
from playwright.async_api import async_playwright

MAIL_TM_API = "https://api.mail.tm"

def create_temp_email():
    domain = requests.get(f"{MAIL_TM_API}/domains").json()["hydra:member"][0]["domain"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    email_address = f"{username}@{domain}"

    register = requests.post(f"{MAIL_TM_API}/accounts", json={"address": email_address, "password": password})
    if register.status_code != 201:
        raise Exception("Failed to create mail.tm account")

    token_res = requests.post(f"{MAIL_TM_API}/token", json={"address": email_address, "password": password})
    token = token_res.json()["token"]
    return email_address, password, token

def get_verification_code(token):
    headers = {"Authorization": f"Bearer {token}"}
    timeout = time.time() + 60
    while time.time() < timeout:
        resp = requests.get(f"{MAIL_TM_API}/messages", headers=headers)
        messages = resp.json()["hydra:member"]
        for msg in messages:
            if "Garena" in msg["from"]["address"]:
                full_msg = requests.get(f"{MAIL_TM_API}/messages/{msg['id']}", headers=headers).json()
                code = "".join(filter(str.isdigit, full_msg["text"]))
                if len(code) == 6:
                    return code
        time.sleep(2)
    raise Exception("Verification code not received")

async def main():
    email, email_pass, token = create_temp_email()
    username = "user" + ''.join(random.choices(string.digits, k=5))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    print(f"Tạo email: {email}")
    print("Đang mở trình duyệt...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://sso.garena.com/universal/register")

        # Nhập email và gửi mã xác nhận
        await page.fill('input[name="email"]', email)
        await page.click("text=Send Code")
        print("Đã gửi yêu cầu gửi mã xác nhận")

        # Chờ mã gửi về mail.tm
        print("Đang đợi mã xác nhận...")
        code = get_verification_code(token)
        print(f"Mã xác nhận: {code}")

        await page.fill('input[name="email_code"]', code)
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.fill('input[name="confirm_password"]', password)

        await page.click("text=Register")
        await page.wait_for_timeout(5000)

        if "register/success" in page.url:
            print("✅ Tạo tài khoản thành công!")
            with open("accounts.txt", "a") as f:
                f.write(f"{email}|{email_pass} | {username}|{password}\n")
            print(f"Email: {email}\nUser: {username}\nPass: {password}")
        else:
            print("❌ Tạo tài khoản thất bại!")

        await browser.close()

asyncio.run(main())