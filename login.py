"""
@Author Hinux Chau
"""
#url: https://stuhealth.jnu.edu.cn

import json
import time
from requests import Session
from email.mime.text import MIMEText
import smtplib
import os

def printd(n):
    print(n)
    exit(2)

#Log
def log(content,is_error:bool):
    with open("./log.txt","a+") as f:
        if is_error:
            f.writelines("**[{0}] ERROR: {1}\n".format(time.asctime(),content))
        else:
            f.writelines("[{0}] {1}\n".format(time.asctime(),content))

#You can customize this function for your email.
def sendmail(content,mail):
    """
    @param content Content to be sent
    @mail Mail address in "stuinfo"
    """
    with open('./sender_email','r+') as f:
        sender_info=json.load(fp=f)
        msg_from=sender_info["email"]                                 #Mailbox of sender
        passwd=sender_info["code"]                                      #Authentication code
    msg_to=mail                                                    #Mailbox of receiver                        
    subject="From:Hinux's Bot"                                     #Subject          　　                                          
    msg = MIMEText(content)                                        #Use the MIMEText to convert the content into correct form
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        #log("Mail has been sent",False)
        s.quit()
    except Exception as e:
        log(str(e),True)

if __name__ == "__main__":
    mail_pot={}
    stu=Session()
    stuinfo={}
    headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'}

    try:
        with open("./mails","r+") as mails:
            mail_pot=json.load(mails)
    except Exception as e:
        sendmail("**[{0}] ERROR!!\n{1}".format(time.asctime(),str(e)),"1624339284@qq.com")

    for m in range(0,len(mail_pot[0])):      #m stands for index of each element
        
        try:
            
            with open("./stuinfo","r+") as f:
                stuinfo=json.load(f)

            login=stu.post(url="https://stuhealth.jnu.edu.cn/api/user/login",json={'username':stuinfo[m]['username'],'password':stuinfo[m]['password']},headers=headers)
            print(f" {stuinfo[m]['username']}:{login.json()['meta']['msg']}")
            if login.json()['meta']['msg']=='登录成功，今天已填写':
                print(f"{stuinfo[m]['username']}:登陆成功，今天已经填写")
                
                sendmail("Hey!User{0} Here is **[{1}]\n{2}".format(stuinfo[m]['username'],time.asctime(),login.json()['meta']['msg']),mail_pot[0][stuinfo[m]['username']])
                #log(login.json()['meta']['msg'],False)

            if login.json()['meta']['msg']=='登录成功，今天未填写':
                #log(login.json()['meta']['msg'],is_error=False)
                with open("payload","r+") as f:
                    payload=json.load(f)
                    
                payload[m]["mainTable"]["declareTime"] = "{0}-{1}-{2}".format(time.localtime().tm_year,time.localtime().tm_mon,time.localtime().tm_mday)
                print(payload[m])
                fill=stu.post(url="https://stuhealth.jnu.edu.cn/api/write/main",json=payload[m],headers=headers)
                print(f"{stuinfo[m]['username']}:{fill.json()['meta']['msg']}")
                sendmail("Good morning!{0} **[{1}]\n{2}".format(stuinfo[m]['username'],time.asctime(),fill.json()['meta']['msg']),mail_pot[0][stuinfo[m]['username']])
                #log(fill.json()['meta']['msg'],False)
                time.sleep(1.5)

        except Exception as e:
            #log(str(e),True)
            sendmail("{0}**[{1}] ERROR!!\n{2}".format(stuinfo[m]['username'],time.asctime(),str(e)),"1624339284@qq.com")
            continue
    
    stu.close()
