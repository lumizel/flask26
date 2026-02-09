# pip install flask
# 플라스크란?
# 파이썬으로 만든 db연동 콘솔 프로그램을 웹으로 연결하는 프레임워크임.
# 프레임워크 : 미리 만들어 놓은 틀 안에서 작업하는 공간
# app.py는 플라스크로 서버를 동작하기 위한 파일명(기본파일)
# static, templates 폴더 필수 (프론트용 파일 모이는 곳)
# static : 정적 파일을 모아 놓음(html, css, js)
# templates : 동적파일을 모아 놓음(crud화면, 레이아웃, index 등...)
from flask import Flask, render_template, request, redirect, url_for, session

from LMS.common import Session

#                 플라스크    프론트 연결   요청,응답   주소전달    주소생성  상태저장소


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
# 세션을 사용하기 위해 보안키 설정 (아무 문자열 입력)

@app.route('/login', methods=['GET','POST'] ) # http://localgost:5000/login
    #                   메서드는 웹에 동작에 관여한다.
    # GET : URL 주소로 데이터를 처리(보안상 좋지 않음, 빠름)
    # POST : BODY 영역에 데이터를 처리함.(보안상 좋음, 대용량일 때 많이 사용함.)
    # 대부분 처음에 화면을(HTML랜더) 요청할 때는 GET 방식으로 처리
    # 화면에 있는 내용을 백엔드로 전달할 땐 POST를 사용함.

def login():
    if request.method == 'GET': # 처음 접속하면 GET 방식으로 화면 출력
        return render_template('login.html') # GET 방식으로 요청하면 login.html 화면이 나옴
        # login.html 에서 action="/login" method = "POST"처리용 코드
        # login.html에서 넘어온 폼 데이터는 uid,upw
    uid = request.form.get('uid') # 요청한 폼내용을 가져옴
    upw = request.form.get('upw')  # request form get
    # print('/login에서 넘어온 폼 데이터 출력 테스트')
    # print(uid, upw)
    # print('='*30)

    conn = Session.get_connection() # 교사용 db에 접속용 객체
    try: # 예외 발생 가능성 있음
        with conn.cursor() as cursor: # db에 커서 객체 사용
            # 1회원 정보 조회
            sql = 'select id,name,uid,role\
                   from members where uid = %s and password = %s'
            #                          uid가 동일 & pwd가 동일
            #         id name uid role 가져온다
            cursor.execute(sql, (uid, upw))  # 쿼리문 실행
            user = cursor.fetchone()  #쿼리 결과 하나 가져오기  -> user 변수에 넣음

            if user :
                # 찾은계정이 있다. -> 브라우저의 세션영역에 보관한다.
                session['user_id'] = user['id'] # 계정 일련번호 (회원번호)
                session['user_name'] = user['name'] # 계정이름
                session['user_uid'] = user['uid']  # 계정 로그인 명
                session['user_role'] = user['role']  #계정 권한
                # 세션에 저장완료
                # 브라우저에서 f12번을 누르고 애플리케이션 탭에서 쿠키 들가서 세션 객체가 보임
                # 쿠키를 삭제하면 로그아웃 처리됨.
                return redirect(url_for('index'))
                # 처리 후 이동하는 경로 http://localhoset:/index 로 감 (get 메서드 방식)
            else:
                # 찾은계정이 없다.
                return "<script> alert('아이디나 비번이 틀렸습니다.);history.back();</script> >"
            #                    경고창                            뒤로가기
    finally:
        conn.close()

@app.route('/logout') # 기본방식이 get방식이라 -> methods=['GET'] 생략 ㅇㅇ
def logout():
    session.clear()
    return redirect(url_for('login')) # 다음 경로로 보내기 로그인 경로로 보내는 리다이렉트 - http://localhost:5000/login (get 방식)

@app.route('/join', methods=['GET','POST']) # 회원가입용 함수
def join(): # http://localhost:5000/ get메서드(화면출력) post(화면폼처리용)
    if request.method == 'GET':
        return render_template('join.html') # 로그인 화면용 프론트 연결

    # POST 메서드일 경우 시 (폼으로 데이터가 넘어올 때 처리)
    uid = request.form.get('uid')
    password = request.form.get('password')
    name = request.form.get('name') # 폼에서 넘어 온 값을 변수에 넣음.

    conn = Session.get_connection()
    try: #예외 발생 가능성이 있는 코드
        with conn.cursor() as cursor:
            cursor.execute('select id from members where uid = %s',(uid,)) # 튜플이라 uid, 콤마 달아둠.
            if cursor.fetchone() :
                return "<script> alert('이미 존재하는 아이디입니다.';history.back();</script> >"

            sql = 'insert into members (uid,password,name) values (%s,%s,%s)'
            cursor.execute(sql, (uid, password, name))
            conn.commit()

            return "<script> alert('가입 완료.');location.href='/login';</script> >"




    except Exception as e: # 예외 발생시 실행문
        print(f'회원가입 에러 : {e}')
        return '가입 중 오류 발생 /n join()를 확인하세요.'
    finally: # 항상 실행문
        conn.close()

@app.route( '/member/edit',methods=['GET','POST'])
def member_edit():
    if 'user_id' not in session: # 세션에 유저 아이디가 없으면
        return redirect(url_for('login'))  # 로그인 경로로 보낸다.

    # 있으면 db 연결
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                # 기존 정보 불러오기
                cursor.execute('select * from members where uid = %s',(session['user_id'],))
                user_info = cursor.fetchone()
                return render_template(template_name_or_list= 'member_edit.html', user=user_info)
                #                      가장 중요한 포인트         get 요청 시 페이지       객체 전달용 코드
            # POST 요청 : 정보 업데이트
            new_name = request.form.get('name')
            new_pw = request.form.get('password')

            if new_pw: # 비밀번호 입력 시에만 변경
                sql = 'update members set name = %s, password = %s where id = %s'
                cursor.execute(sql, (new_name,new_pw, session['user_id']))
            else: # 이름만 변경
                sql = 'update members set name = %s where id = %s'
                cursor.execute(sql, (new_name, session['user_id']))

            conn.commit()
            session['user_name'] = new_name
            return "<script> alert('정보 수정 완료.'); location.href='/mypage';</script> "

    except Exception as e:
        print(f'회원수정 에러 : {e}')
        return '수정 중 오류 발생 /n member_edit()를 확인하세요.'

    finally:
        conn.close()


@app.route('/') # url 생성용 코드 http://localhost:5000/ 내ip:5000/ http://192.168.0.175:5000/
def index():
    return render_template('main.html')
    # render_template 웹브라우저로 보낼 파일명
    # templates라는 폴더에서 main,html을 찾아 보냄.

@app.route('/mypage') # http://localhoset5000/mypage get요청
def mypage():
    if 'user_id' not in session:# 로그인 상태 확인
        return redirect(url_for('login')) # 로그인 상태 아니면 로그인으로 보냄 http://localhoset5000/ㅣㅐ햐ㅜ

    conn = Session.get_connection() # db연결
    try:
        with conn.cursor() as cursor:
            # 1. 내 상세 정보 조회
            cursor.execute('select * from members where id = %s',(session['user_id'],))
            # 로그인한 정보를 가지고 db에서 찾아옴
            user_info = cursor.fetchone() # 찾아온 값 한개를 변수에 넣음. (dict 타입)

            # 2. 내가 쓴 게시글 개수 조회(작성하신 boards 테이블 활용)
            cursor.execute('select count(*) as board_count from boards where member_id = %s',(session['user_id'],))
            #                                                   보드 테이블에 있는 멤버 아이디 값을 가지고 찾음
            #           찾은 후 갯수를 세어 fetchone에 넣음 -> board_count 이름으로 개수를 가지고 있음.

            board_count = cursor.fetchone()['board_count']

            return render_template(template_name_or_list= 'mypage.html', user=user_info, board_count=board_count)
            # 결과 리턴                                           여기에 user 객체와 board_count 객체를 담아 보냄
            # 프론트에서 사용하려면 {{user.???}} {{board_count}}로 사용함.

    finally:
        conn.close()





if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
    #    hose=0.0.0.0 -> 누가 요청하던 응답하라
    #    port = 5000 플라스크에서 사용하는 포트번호
    #    debug=True 콘솔에 디버그를 보겠다.