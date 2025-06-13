from flask import Flask
import OrgSQLRepository as orgSql
orgSql.config()

app=Flask(__name__)
honeytoken_data=orgSql.get_honey_tokens()
data_list=[]
for i in range(len(honeytoken_data)):
    current_data={}
    email=str(honeytoken_data[i])
    current_data['email']=email[2:-3]
    data_list.append(current_data)

blocked_email_data=orgSql.blocked_emails()
print(blocked_email_data[0][1])
blocked_email=[] 
for i in range(len(blocked_email_data)):
    current_data={}
    email=str(blocked_email_data[i])
    current_data['attacker']=str(blocked_email_data[i][0])
    current_data['title']=str(blocked_email_data[i][1])[1:]
    current_data['body']=str(blocked_email_data[i][2])
    current_data['honeytoken']=str(blocked_email_data[i][3])
    blocked_email.append(current_data)
org_list=orgSql.org_emails()
spam_email=[]
for i in range(len(org_list)):
    current_data={}
    email=str(org_list[i])
    current_data['attacker']=str(org_list[i][0])
    current_data['title']=str(org_list[i][1])[1:]
    current_data['body']=str(org_list[i][2])
    current_data['to']=str(org_list[i][3])
    spam_email.append(current_data)
@app.route("/honeytoken")
def honeytoken():
    return data_list
@app.route("/blockedEmail")
def blockedEmail():
    return blocked_email
@app.route("/orgEmails")
def orgEmails():
    return spam_email
    #return org_list
if __name__=="__main__":
    app.run(debug=True)
