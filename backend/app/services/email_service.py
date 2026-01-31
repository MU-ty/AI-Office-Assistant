import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
import os
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class EmailService:
    """邮件发送服务"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM

    def send_email(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        attachments: Optional[List[str]] = None,
        content_type: str = "plain"
    ) -> bool:
        """
        发送邮件
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            content: 邮件内容
            attachments: 附件路径列表
            content_type: 内容类型 ("plain" or "html")
            
        Returns:
            bool: 发送是否成功
        """
        if not self.smtp_server or not self.smtp_user:
            logger.warning("SMTP配置未完成，无法发送邮件")
            return False

        msg = MIMEMultipart()
        msg['From'] = self.smtp_from
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        # 添加正文
        msg.attach(MIMEText(content, content_type))

        # 添加附件
        if attachments:
            for file_path in attachments:
                if not os.path.exists(file_path):
                    logger.warning(f"附件不存在: {file_path}")
                    continue
                    
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                    
                    # Add header for attachments
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
                except Exception as e:
                    logger.error(f"添加附件失败 {file_path}: {e}")

        try:
            # 连接SMTP服务器
            if self.smtp_port == 465:
                # SSL连接
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # 普通连接 + STARTTLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()

            # 登录
            server.login(self.smtp_user, self.smtp_password)
            
            # 发送
            server.sendmail(self.smtp_from, recipients, msg.as_string())
            server.quit()
            
            logger.info(f"邮件发送成功: {subject} -> {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

# 单例实例
email_service = EmailService()
