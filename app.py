from flask import Flask,  render_template,  session, redirect, request
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


app = Flask(__name__)
app.secret_key = b'abcdefg'




#heroku postgres shelterremake 新しいherokuDB　（元shelter2）
engine = create_engine('postgresql:/')


Base = declarative_base()

#データベース(shelter)につなげる tableの名前は houseowner
class HouseOwner(Base):
    __tablename__ = "houseowner"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstnameho = Column(String(255))
    lastnameho = Column(String(255))
    groupho = Column(String(255))
    pswdho = Column(String(255))
    mailho = Column(String(255))
    callnumho = Column(String(255))



    def __init__(self,  firstnameho, lastnameho, groupho, pswdho, mailho, callnumho):
        self.firstnameho = firstnameho
        self.lastnameho = lastnameho
        self.groupho = groupho
        self.pswdho = pswdho
        self.mailho = mailho
        self.callnumho = callnumho


#ユーザー登録情報
class User(Base):
    __tablename__ = "houseuser"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstnameuser = Column(String(255))
    lastnameuser = Column(String(255))
    groupuser = Column(String(255))
    pswduser = Column(String(255))
    mailuser = Column(String(255))
    callnumuser = Column(String(255))

    def __init__(self, firstnameuser, lastnameuser, groupuser, pswduser, mailuser, callnumuser):
        self.firstnameuser = firstnameuser
        self.lastnameuser = lastnameuser
        self.groupuser = groupuser
        self.pswduser = pswduser
        self.mailuser = mailuser
        self.callnumuser = callnumuser

#HOUSEOWNER　POST HOUSE
class OwnerPost(Base):
    __tablename__ = "ownerpost"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    OwnerGroup = Column(String(255))
    OwnerGoogleMap = Column(String(500))
    OwnerPrefecture = Column(String(255))
    OwnerCity = Column(String(255))
    OwnerOther = Column(String(255))

    def __init__(self, OwnerGroup, OwnerGoogleMap, OwnerPrefecture, OwnerCity, OwnerOther):
        self.OwnerGroup = OwnerGroup
        self.OwnerGoogleMap = OwnerGoogleMap
        self.OwnerPrefecture = OwnerPrefecture
        self.OwnerCity = OwnerCity
        self.OwnerOther = OwnerOther


# USER REQUEST HOUSE
class UserRequest(Base):
    __tablename__ = "userrequest"  # テーブル名を指定
    id = Column(Integer, primary_key=True, autoincrement=True)
    UserGroup = Column(String(255))
    UserGoogleMap = Column(String(500))
    UserOwnerName = Column(String(255))

    def __init__(self, UserGroup, UserGoogleMap, UserOwnerName):
        self.UserGroup = UserGroup
        self.UserGoogleMap = UserGoogleMap
        self.UserOwnerName = UserOwnerName




Base.metadata.create_all(engine)



@app.route('/', methods=['GET'])
def index():
    return render_template('first.html')


@app.route('/house', methods=['GET'])
def house():
    Session = sessionmaker(bind=engine)
    ses = Session()
    housedatas = ses.query(OwnerPost).all()

    ses.close()

    return render_template('house.html', housedatas=housedatas)



#新規登録 Sign Up
@app.route('/new/houseowner', methods=['GET','POST'])
def newhouseowner(): #データ入力をｄｂに保存　ログイン完成
    if request.method == 'POST':
        firstnewho = request.form.get('firstnewho')
        lastnewho = request.form.get('lastnewho')
        groupnewho = request.form.get('groupnewho')
        pswdnewho = request.form.get('pswdnewho')
        mailho = request.form.get('mailho')
        callnumho = request.form.get('callnumho')

        newownerdata = HouseOwner(firstnameho=firstnewho, lastnameho=lastnewho, groupho=groupnewho, pswdho=pswdnewho,
                                  mailho=mailho, callnumho=callnumho)

        Session = sessionmaker(bind=engine)
        ses = Session()
        hologindatas = ses.query(HouseOwner).filter(HouseOwner.firstnameho == firstnewho,
                                                       HouseOwner.lastnameho == lastnewho,
                                                       HouseOwner.groupho == groupnewho,
                                                       HouseOwner.pswdho == pswdnewho).all()


        if hologindatas:
            alreadymsg = "既に登録いただいています。お家を登録する　のボタンからログインが可能です!"
            ses.close()
            session['login'] = False
            return render_template('first.html', alreadymsg=alreadymsg, already=True)
        else:

            #被らない情報をテーブルにコミット
            ses.add(newownerdata)
            ses.commit()
            ses.close()
            session['login'] = True
            session['hogroupind'] = groupnewho


            return redirect('/login/hopost')


#ログイン
@app.route('/login/houseowner', methods=['GET', 'POST'])
def houseowner(): #送信したデータをＤＢと照合させてあってたらログイン　まちがっていたらログインもう一度

    if request.method == 'POST':
        grouplogho = request.form.get('grouplogho')
        pswdlogho = request.form.get('pswdlogho')

        Session = sessionmaker(bind=engine)
        ses = Session()
        logindatas = ses.query(HouseOwner).filter(HouseOwner.groupho == grouplogho, HouseOwner.pswdho == pswdlogho).all()
        ses.close()

        if logindatas: #変えるsession['login'] = True
            session['login'] = True
            session['hogroupind'] = grouplogho #session[hogroupind]にグループ名を保存し、 OwnerPost.OwnerGroupで登録するのに使う
            return redirect('/login/hopost')

        else:#このまま　forst.htmlh当時
            session['login'] = False
            wrongmsg = "団体名もしくはパスワードがちがいます。もう一度ログインお願いいたします。"
            return render_template('first.html', alreadymsg=wrongmsg, already=True)






#loginページでのポスト情報
@app.route('/login/hopost', methods=['GET', 'POST'])
def hopost():
    if request.method == 'GET': #hoログイン時のページ表示
        if 'login' in session and session['login']:
            msg = "こんにちは！" + "　" + session['hogroupind'] + 'さん'
            Session = sessionmaker(bind=engine)
            ses = Session()
            houseind = ses.query(OwnerPost).filter(OwnerPost.OwnerGroup == session['hogroupind']).all()

            housedatas = ses.query(OwnerPost).all()

            ses.close()
            return render_template('houseowner.html', title='Login Page: HouseOwner', newmessage=msg, houseind=houseind, housedatas=housedatas)
        else:
            return redirect('/')


    elif request.method == 'POST': #ログイン内のpost request DBに保存
        # HouseOwner House情報POST 保存　DB: shelter table:OwnerPost

        hogroupind = session['hogroupind']
        hogooglem = request.form.get('hogooglem')
        hoprefecture = request.form.get('hoprefecture')
        hocity = request.form.get('hocity')
        hoother = request.form.get('hoother')

        ownerpostedall = OwnerPost(OwnerGroup=hogroupind,
                                   OwnerGoogleMap=hogooglem,
                                   OwnerPrefecture=hoprefecture,
                                   OwnerCity=hocity,
                                   OwnerOther=hoother)

        Session = sessionmaker(bind=engine)
        ses = Session()
        ses.add(ownerpostedall)
        ses.commit()
        # ログインしているユーザーのindivisual　housepostをとりだす
        houseind = ses.query(OwnerPost).filter(OwnerPost.OwnerGroup == session['hogroupind']).all()
        housedatas = ses.query(OwnerPost).all()

        ses.close()

        newmessage = "お家の登録ありがとうございます！" + session['hogroupind'] + "さん"

        return render_template('houseowner.html', houseind=houseind, newmessage=newmessage, housedatas=housedatas)





#新規登録　Sign Up
@app.route('/new/user', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        firstnewuser = request.form.get('firstnewuser')
        lastnewuser = request.form.get('lastnewuser')
        groupnewuser = request.form.get('groupnewuser')
        pswdnewuser = request.form.get('pswdnewuser')
        emailuser = request.form.get('emailuser')
        calluser = request.form.get('calluser')


        newuserdata = User(firstnameuser=firstnewuser, lastnameuser=lastnewuser, groupuser=groupnewuser, pswduser=pswdnewuser,
                                  mailuser=emailuser, callnumuser=calluser)

        Session = sessionmaker(bind=engine)
        ses = Session()

        userlogindatas = ses.query(User).filter(User.firstnameuser == firstnewuser,
                                                       User.lastnameuser == lastnewuser,
                                                       User.groupuser == groupnewuser,
                                                       User.pswduser == pswdnewuser).all()

        if userlogindatas:
            alreadymsg = "既に登録いただいています。ユーザーのログインが可能です!"
            ses.close()
            return render_template('first.html', alreadymsg=alreadymsg, already=True)
        else:
            newmessage = "登録ありがとうございます！　ようこそ" + groupnewuser + "さん"

            #被らない情報をテーブルにこみっと
            ses.add(newuserdata)
            ses.commit()
            ses.close()
            session['login'] = True

            session['usergroupind'] = groupnewuser

            return redirect('/login/postreq')





#ログイン
@app.route('/login/user', methods=['GET', 'POST'])
def loginuser():
    if request.method == 'POST':
        grouploguser = request.form.get('grouploguser')
        pswdloguser = request.form.get('pswdloguser')

        Session = sessionmaker(bind=engine)
        ses = Session()
        loginuser = ses.query(User).filter(User.groupuser == grouploguser, User.pswduser == pswdloguser).all()
        ses.close()


        if loginuser:
            session['login'] = True
            session['usergroupind'] = grouploguser
            return redirect('/login/postreq')
        else:
            session['login'] =  False
            wrongmsg = "団体名もしくはパスワードがちがいます。もう一度ユーザーのログインお願いいたします。"
            return render_template('first.html', alreadymsg=wrongmsg, already=True)




#ログインページ内のポストリクエスト
@app.route('/login/postreq', methods=['GET', 'POST'])
def postreq():
    if request.method == 'GET': #ログイン時のページ表示
        if 'login' in session and session['login']:
            msg = "こんにちは！" + "　" + session['usergroupind'] + "さん"
            Session = sessionmaker(bind=engine)
            ses = Session()

            postreqind = ses.query(UserRequest).filter(UserRequest.UserGroup == session['usergroupind']).all() #session['usergroupind']に　UserGroupをいれる

            housedatas = ses.query(OwnerPost).all()

            ses.close()
            return render_template('user.html', title='UserPosted Page', newmessage=msg, postreqind=postreqind, housedatas=housedatas)
        else:
            return redirect('/')


    elif request.method == 'POST': #ログイン内のpost request DBに保存
        # userrequest tableに保存
        usergoogle = request.form.get('usergoogle')
        usertoowner = request.form.get('usertoowner')

        userrequestall = UserRequest(UserGroup=session['usergroupind'], UserGoogleMap=usergoogle, UserOwnerName=usertoowner)
        Session = sessionmaker(bind=engine)
        ses = Session()
        ses.add(userrequestall)
        ses.commit()
        # ログインしているユーザーのindivisual　リクエストをとりだす
        postreqind = ses.query(UserRequest).filter(UserRequest.UserGroup == session['usergroupind']).all()
        housedatas = ses.query(OwnerPost).all()

        ses.close()
        newmessage = 'リクエストありがとうございます' + session['usergroupind'] + 'さん'


        return render_template('user.html', postreqind=postreqind, newmessage=newmessage, housedatas= housedatas)





if __name__ == '__main__':
    app.run(debug=True)
