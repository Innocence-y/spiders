import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
#settings里面的常量 管理员邮箱 密码 项目根目录
from settings import ADMINEMAIL,ADMINEMAILPASSWORD,BASE_DIR
#database包下面 Mydb.py里面封装的MySQLConn类
from database.Mydb import MySQLConn

#用户邮箱激活 /user/activate 用户名 用户邮箱 激活码 发送到用户邮件
class EmailActive(MySQLConn):
    def __init__(self,user_name,user_email,active_code):
        self.user_name = user_name
        self.user_email = user_email
        self.active_code = active_code

    def send_active_email(self):
        #msg = MIMEMultipart('alternative')'related'
        msg = MIMEMultipart('related')
        msg['Subject'] = "python fan 邮箱激活"
        msg['From'] = ADMINEMAIL
        msg['To'] = self.user_eamil
        html = """
        <html>
          <head></head>
          <body>
            <p>{}:<br>
            <hr>
            &nbsp&nbsp.恭喜您在python fan 注册成功!<br>
            &nbsp&nbsp.您的激活码是:<span style="color: darksalmon">{}</span><br>
            &nbsp&nbsp.请您在24小时内激活邮箱,激活之后方可以查看网站其他的内容.<br>
            &nbsp&nbsp.网站地址:<a href="http://www.pythonfan.net">http://www.pythonfan.net</a><br>
            &nbsp&nbsp.欢迎您微信扫描下面二维码关注我们的微信公众号:pythonfan<br>
            <hr>
               <img class="loading" src="cid:image1"><br>
            </p>
          </body>
        </html>
        """
        mail_html = MIMEText(html.format(self.user_name, self.active_code), 'html','utf-8')
        msg.attach(mail_html)
        # 公众号图片:
        weixin_pic_path = os.path.join(BASE_DIR, 'statics/images/weixingongzhong.jpg')
        print(weixin_pic_path)
        fp = open(weixin_pic_path, 'rb')
        msgImage = MIMEImage(fp.read())
        msgImage.add_header('Content-ID', '<image1>')
        fp.close()
        msg.attach(msgImage)
        s = smtplib.SMTP('smtp.163.com', 25)
        s.login(ADMINEMAIL, ADMINEMAILPASSWORD)
        s.sendmail(ADMINEMAIL, self.user_eamil, msg.as_string())
        s.quit()
        return True

    def __str__(self):
        return self.user_name

if __name__ == '__main__':
    acti = EmailActive('cxy','chengxinyao1991@163.com','python fan test')
    print(acti)
    info = acti.send_active_email()
    print(info)
