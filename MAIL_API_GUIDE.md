# Aetheria AI 邮件服务调用指南

本文档提供了如何通过程序调用已部署的 `docker-mailserver` 服务的详细说明。

## 1. 服务连接信息

| 协议 | 端口 | 安全加密方式 | 说明 |
| :--- | :--- | :--- | :--- |
| **SMTP** | 465 | SSL/TLS (Implicit) | **推荐发信端口** |
| **SMTP** | 587 | STARTTLS (Explicit) | 备选发信端口 |
| **IMAP** | 993 | SSL/TLS (Implicit) | 收信协议 (IMAP) |
| **POP3** | 995 | SSL/TLS (Implicit) | 收信协议 (POP3) |

- **服务器地址**: `mail.aetheriaai.cn` (外部) 或 `127.0.0.1` (本地)
- **默认账户**: `admin@aetheriaai.cn`
- **默认密码**: `AetheriaMail2025!`

---

## 2. Python 调用示例

使用内置 `smtplib` 库发送邮件。

```python
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ssl

def send_mail(subject, content, to_email):
    smtp_server = "mail.aetheriaai.cn"
    smtp_port = 465
    sender_email = "admin@aetheriaai.cn"
    sender_password = "AetheriaMail2025!"
    sender_name = "Aetheria AI"

    # 构建邮件
    message = MIMEText(content, "plain", "utf-8")
    message["From"] = f'{Header(sender_name, "utf-8").encode()} <{sender_email}>'
    message["To"] = to_email
    message["Subject"] = Header(subject, "utf-8")

    # SSL 上下文 (如果证书未在系统信任链中，可设置 verify_mode=ssl.CERT_NONE)
    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], message.as_string())
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# 使用
send_mail("测试主题", "这是邮件正文内容", "target@example.com")
```

---

## 3. Node.js (Nodemailer) 调用示例

```javascript
const nodemailer = require("nodemailer");

async function main() {
  let transporter = nodemailer.createTransport({
    host: "mail.aetheriaai.cn",
    port: 465,
    secure: true, // 使用 SSL
    auth: {
      user: "admin@aetheriaai.cn",
      pass: "AetheriaMail2025!",
    },
  });

  let info = await transporter.sendMail({
    from: '"Aetheria AI" <admin@aetheriaai.cn>',
    to: "target@example.com",
    subject: "Hello from Aetheria AI",
    text: "这是一封测试邮件",
  });

  console.log("Message sent: %s", info.messageId);
}

main().catch(console.error);
```

---

## 4. 管理命令

在服务器上通过 Docker 执行管理操作：

- **添加账号**:
  ```bash
  docker exec -it mailserver setup email add <user@aetheriaai.cn> <password>
  ```
- **更改密码**:
  ```bash
  docker exec -it mailserver setup email update <user@aetheriaai.cn> <new_password>
  ```
- **查看账号列表**:
  ```bash
  docker exec -it mailserver setup email list
  ```
- **重新生成 DKIM 记录**:
  ```bash
  docker exec -it mailserver setup config dkim
  ```

---

## 5. DNS 配置回顾 (重要)

为确保邮件不进入垃圾箱，请确保 DNS 包含以下 TXT 记录：

- **SPF**: `v=spf1 mx ip4:115.190.170.8 ~all`
- **DMARC**: `v=DMARC1; p=none;`
- **DKIM**: 主机记录 `mail._domainkey`，值详见部署日志或 `docker-data/dms/config/opendkim/keys/aetheriaai.cn/mail.txt`。
