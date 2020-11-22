import sqlite3
from flask import Flask, jsonify, json, request
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

'''
获取座位列表
'''
@app.route('/seat/info', methods=['POST', 'GET'])
def all_seat_info():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    info = dict()

    sql = '''select * from seat_info'''
    cursor.execute(sql)
    listexample = cursor.fetchall()

    if len(listexample) == 0:
        info['statusCode'] = 400
    else:
        info['statusCode'] = 200
        data = dict()
        seats = []
        for i in range(len(listexample)):
            seat_data_feed = dict()
            seat_id, user_id, seat_status, seat_type, seat_row, seat_col = listexample[i]
            seat_data_feed['seatID'] = seat_id
            seat_data_feed['seatStatus'] = seat_status
            seat_data_feed['seatType'] = seat_type
            seat_data_feed['seatRow'] = seat_row
            seat_data_feed['seatCol'] = seat_col
            seats.append(seat_data_feed)
        data['seats'] = seats
        info['data'] = data

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(info)


'''
在选座终端登录
'''
@app.route('/login', methods=['POST', 'GET'])
def login_lib():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    accept_data = json.loads(request.get_data())
    stu_id = accept_data['studentID']
    info = dict()

    sql = '''select student_name from student_info where (student_id=:stu_id_toFeed)'''
    cursor.execute(sql, {'stu_id_toFeed':stu_id})
    listexample = cursor.fetchall()
    if len(listexample) == 0:   # 查无此人，登陆失败
        info['statusCode'] = 400
    else:
        info['statusCode'] = 200
        data = dict()
        data['studentID'] = stu_id
        data['studentName'] = listexample[0][0]
        info['data'] = data

    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(info)

'''
进入图书馆
'''
@app.route("/enterLib", methods=['POST', 'GET'])
def enter_lib():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())
    stu_id = accept_data['studentID']

    sql = '''select * from student_info where (student_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})

    if len(cursor.fetchall()) == 0:     # 找不到该学生，无权限进入图书馆
        info = dict()
        info['statusCode'] = 400
        return jsonify(info)

    else:
        info = dict()
        data = dict()
        info['statusCode'] = 200
        data['studentID'] = stu_id
        info['data'] = data
        
        sql = '''select seat_id from seat_leave_briefly where (user_id=:user_id_toFeed)'''
        cursor.execute(sql, {'user_id_toFeed': stu_id})

        if len(cursor.fetchall()) != 0:     #在短暂离席表中查询这个人，如果有，删除短暂离席，插入到座位信息中，如果没有什么都不用做

            sql = '''update seat_info set seat_status=1 where seat_info."user_id"=''' + (str(stu_id))
            cursor.execute(sql)

            sql = '''delete from seat_leave_briefly where (user_id=:user_id_toFeed)'''
            cursor.execute(sql, {'user_id_toFeed': stu_id})

            conn.commit()
            cursor.close()
            conn.close()

        return jsonify(info)

'''
离开图书馆
'''
@app.route('/leaveLib', methods=['POST', 'GET'])
def leave_lib():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    info = dict()

    accept_data = json.loads(request.get_data())
    stu_id = accept_data['studentID']

    sql = '''select * from student_info where (student_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})

    if len(cursor.fetchall()) == 0:     # 找不到该学生，无权限进入图书馆
        info = dict()
        info['statusCode'] = 400
        return jsonify(info)

    else:
        info['statusCode'] = 200
        data = dict()
        data['studentID'] = stu_id
        info['data'] = data

        sql = '''select seat_id from seat_info where (user_id=:user_id_toFeed)'''
        cursor.execute(sql, {'user_id_toFeed': stu_id})
        listexample = cursor.fetchall()
        if len(listexample) != 0:
            sql = '''select * from seat_leave_briefly where (user_id=:user_id_toFeed)'''
            cursor.execute(sql, {'user_id_toFeed': stu_id})
            is_leave_briefly = cursor.fetchall()
            if len(is_leave_briefly) == 0:
                sql = '''update seat_info set seat_status=0, user_id=-1 where (user_id=:user_id_toFeed)'''
                cursor.execute(sql, {'user_id_toFeed': stu_id})

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(info)


'''
主动释放
'''
@app.route('/seat/release', methods=['POST', 'GET'])
def seat_release():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    info = dict()

    accept_data = json.loads(request.get_data())
    stu_id = accept_data['studentID']

    sql = '''select seat_id from seat_info where (user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})
    listexample = cursor.fetchall()
    if len(listexample) == 0:
        info['statusCode'] = 400    # 该student在进入图书馆时，没有选座，因此不存在seat_info当中
    else:
        info['statusCode'] = 200
        sql = '''update seat_info set seat_status=0, user_id=-1 where (user_id=:user_id_toFeed)'''      # 更改座位状态为未使用
        cursor.execute(sql, {'user_id_toFeed': stu_id})
        sql = '''delete from seat_leave_briefly where (user_id=:user_id_toFeed)'''     # 删除暂时离席表中的记录
        cursor.execute(sql, {'user_id_toFeed': stu_id})

    data = dict()
    data['studentID'] = stu_id
    info['data'] = data

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(info)

'''
短暂离席
'''
@app.route('/seat/leave', methods=['POST', 'GET'])
def leave_briefly():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())
    
    stu_id = accept_data['studentID']
    info = dict()

    sql = '''select seat_id from seat_info where(user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})
    listexample = cursor.fetchall()

    if len(listexample) == 0:   # 该学生没有事先在seat_info中占座
        info['statusCode'] = 400
    else:
        info['statusCode'] = 200

        # 防止在 seat_leave_briefly 重复插入
        sql = '''select * from seat_leave_briefly where(user_id=:user_id_toFeed)'''
        cursor.execute(sql, {'user_id_toFeed': stu_id})
        resultLeaveBriefly = cursor.fetchall()
        
        if len(resultLeaveBriefly) == 0:
            seat_id = listexample[0][0]
            sql = '''insert into seat_leave_briefly
                    (id, seat_id, user_id, leave_time)
                    values
                    (null , :seat_id, :user_id, datetime('now', 'localtime'))'''
            cursor.execute(sql, {'seat_id': seat_id, 'user_id': stu_id})    # 实现了主件id的顺序递增插入（修改了数据库表属性）

            sql = '''update seat_info set seat_status=2 where seat_info."user_id"='''+(str(stu_id))
            cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()

    data = dict()
    data['studentID'] = stu_id
    info['data'] = data
    return jsonify(info)

'''
查询用户是否有座位
'''
@app.route('/seat/studentSeat', methods=['POST', 'GET'])
def search_stu_seat():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())

    stu_id = accept_data['studentID']
    info = dict()

    sql = '''select student_name from student_info where (student_id=:student_id_toFeed)'''
    cursor.execute(sql, {'student_id_toFeed': stu_id})
    stu_name = cursor.fetchall()
    stu_name = stu_name[0][0]

    sql = '''select seat_id, seat_status, seat_type, seat_row, seat_col
             from seat_info where (user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})
    listexample = cursor.fetchall()

    if len(listexample) == 0:
        info['statusCode'] = 400    # seat_info中查无此人，暂时选择返回400：携带参数错误（建议修改返回码，或重新指定返回码规则）
        data = dict()
        data['studentID'] = stu_id
        data['studentName'] = stu_name
        info['data'] = data
    else:
        info['statusCode'] = 200    # seat_info中有此人座位记录，返回data中包括'user_id','seat_id','seat_status'
        select_seat_id, select_seat_status, select_seat_type, select_seat_row, select_seat_col = listexample[0]
        data = dict()
        data['studentID'] = stu_id
        data['studentName'] = stu_name
        seat_data = dict()
        seat_data['seatID'] = select_seat_id
        seat_data['seatStatus'] = select_seat_status
        seat_data['seatType'] = select_seat_type
        seat_data['seatRow'] = select_seat_row
        seat_data['seatCol'] = select_seat_col
        data['seat'] = seat_data
        info['data'] = data

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(info)


'''
用户选座
note: seat_info中已存储所有座位的信息，用seat_status区分当前座位的使用状态
      如果无人使用该座位，seat_info表中的'user_id'是否具有初始化值？
'''
@app.route('/seat/select', methods=['POST', 'GET'])
def select_seat():
    conn = sqlite3.connect('feedback.db')  # 数据库名字
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())
    stu_id = accept_data['studentID']
    seat_id = accept_data['seatID']
    info = dict()
    sql = '''select seat_status, seat_type from seat_info where (seat_id=:seat_id_toFeed)'''
    cursor.execute(sql, {'seat_id_toFeed': seat_id})
    listexample = cursor.fetchall()

    if len(listexample) == 0 or listexample[0][0] != 0 or listexample[0][1] == 0:
        info['statusCode'] = 400  # 查找失败（前端seat_id非法）或者该seat_id座位已被占用，或者seat_id所指座位标记为损坏，返回400
    else:
        info['statusCode'] = 200  # 查找成功
        sql = '''update seat_info set seat_status=1, user_id=:stu_id_toFeed where (seat_id=:seat_id_toFeed)'''
        cursor.execute(sql, {'stu_id_toFeed': stu_id, 'seat_id_toFeed': seat_id})

    data = dict()
    data['studentID'] = stu_id
    data['seatID'] = seat_id
    info['data'] = data

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(info)


'''
短暂离席超过20分钟则自动释放座位
scheduler的job的trigger='interval'会一直在后台循环执行
'''
def task_seat_release_overtime():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    sql = '''select seat_id from seat_leave_briefly where leave_time < (select datetime('now','localtime','-60 minutes'))'''
    cursor.execute(sql)
    listexample = cursor.fetchall()
    for i in range(len(listexample)):
        seat_id_to_release = listexample[i][0]
        sql_update = '''update seat_info set seat_status=0, user_id=-1 where seat_id=:seat_id_toFeed'''
        cursor.execute(sql_update, {'seat_id_toFeed':seat_id_to_release})

    seat_release = '''delete from seat_leave_briefly where leave_time < (select datetime('now','localtime','-60 minutes'))'''

    cursor.execute(seat_release)
    conn.commit()
    cursor.close()
    conn.close()
    # print('end one time!')


@app.route('/seat/releaseOvertime', methods=['POST', 'GET'])
def seat_release_overtime():
    scheduler.add_job(func=task_seat_release_overtime, id='1', trigger='interval', seconds=10, replace_existing=True)
    return 'success'    # 返回值，按需调整；不设返回值则报错


if __name__ == '__main__':
    scheduler.init_app(app=app)
    scheduler.start()
    app.run()
