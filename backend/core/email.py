import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 从环境变量获取配置
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SENDER_NAME = os.getenv("SENDER_NAME", "Aetheria AI")

def send_email(to_email: str, subject: str, content: str, subtype: str = "plain") -> bool:
    """
    发送邮件工具函数
    :param to_email: 接收者邮箱
    :param subject: 邮件主题
    :param content: 邮件内容
    :param subtype: 内容类型, plain 或 html
    :return: 是否发送成功
    """
    # 构建邮件
    message = MIMEText(content, subtype, "utf-8")
    message["From"] = f'{Header(SENDER_NAME, "utf-8").encode()} <{SENDER_EMAIL}>'
    message["To"] = to_email
    message["Subject"] = Header(subject, "utf-8")

    # SSL 上下文
    context = ssl.create_default_context()
    
    # 修复 Hostname mismatch 问题：跳过主机名检查和证书验证
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            logger.info("Logging in...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            logger.info(f"Sending email to {to_email}...")
            server.sendmail(SENDER_EMAIL, [to_email], message.as_string())
            logger.info("Email sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_verification_code_email(to_email: str, code: str, expires_in_minutes: int = 5) -> bool:
    """
    发送验证码邮件（HTML 商业化样式）
    """
    subject = f"【{SENDER_NAME}】您的验证码是 {code}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 40px 20px;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333;
                background-color: #f9f9f9;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #4f46e5;
                text-decoration: none;
            }}
            .title {{
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 20px;
                color: #1f2937;
            }}
            .code-container {{
                background-color: #f3f4f6;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                margin: 30px 0;
            }}
            .code {{
                font-size: 36px;
                font-weight: 800;
                letter-spacing: 8px;
                color: #4f46e5;
                margin: 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 13px;
                color: #9ca3af;
                line-height: 1.6;
            }}
            .divider {{
                height: 1px;
                background-color: #e5e7eb;
                margin: 30px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="header">
                    <div class="logo">{SENDER_NAME}</div>
                </div>
                <div class="title">验证您的电子邮箱</div>
                <p>您好！</p>
                <p>感谢您选择 {SENDER_NAME}。请使用下方的验证码来完成注册或身份验证：</p>
                
                <div class="code-container">
                    <div class="code">{code}</div>
                </div>
                
                <p>该验证码将在 <strong>{expires_in_minutes} 分钟</strong> 后失效。为了您的账号安全，请勿将验证码转发给他人。</p>
                
                <div class="divider"></div>
                
                <div class="footer">
                    这是系统自动发送的邮件，请勿直接回复。<br>
                    如果您没有请求此代码，请忽略此邮件。
                </div>
            </div>
            <div class="footer">
                &copy; 2025 {SENDER_NAME}. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_content, subtype="html")

def send_password_reset_email(to_email: str, reset_token: str, expires_in_minutes: int = 30) -> bool:
    """
    发送重置密码邮件（HTML 商业化样式）
    """
    # 假设前端重置密码页面的 URL
    # 在实际项目中，这通常从配置文件或环境变量中获取
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    subject = f"【{SENDER_NAME}】请重置您的密码"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 40px 20px;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333;
                background-color: #f9f9f9;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #4f46e5;
                text-decoration: none;
            }}
            .title {{
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 20px;
                color: #1f2937;
            }}
            .btn-container {{
                text-align: center;
                margin: 30px 0;
            }}
            .btn {{
                background-color: #4f46e5;
                color: #ffffff !important;
                padding: 14px 32px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                display: inline-block;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 13px;
                color: #9ca3af;
                line-height: 1.6;
            }}
            .divider {{
                height: 1px;
                background-color: #e5e7eb;
                margin: 30px 0;
            }}
            .link-info {{
                font-size: 12px;
                color: #6b7280;
                word-break: break-all;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="header">
                    <div class="logo">{SENDER_NAME}</div>
                </div>
                <div class="title">重置您的密码</div>
                <p>您好！</p>
                <p>我们收到了重置您 {SENDER_NAME} 账号密码的请求。请点击下方按钮来设置新密码：</p>
                
                <div class="btn-container">
                    <a href="{reset_link}" class="btn">立即重置密码</a>
                </div>
                
                <p>该链接将在 <strong>{expires_in_minutes} 分钟</strong> 后失效。如果您没有请求重置密码，请忽略此邮件，您的账号依然安全。</p>
                
                <div class="divider"></div>
                
                <div class="footer">
                    这是系统自动发送的邮件，请勿直接回复。<br>
                    如果您点击按钮遇到困难，请复制下方链接到浏览器访问：
                </div>
                <div class="link-info">
                    {reset_link}
                </div>
            </div>
            <div class="footer">
                &copy; 2025 {SENDER_NAME}. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_content, subtype="html")
