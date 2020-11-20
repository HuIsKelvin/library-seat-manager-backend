import sqlite3
from flask import Flask, jsonify, json, request

app = Flask(__name__)

'''
进入图书馆
'''
@app.route("/enterlib", methods=['POST', 'GET'])
def enter_lib():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())

    stu_id = accept_data['studentID']

    sql = '''select seat_id from seat_leave_briefly where (user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})

    if len(cursor.fetchall()) != 0:     #在短暂离席表中查询这个人，如果有，删除短暂离席，插入到座位信息中，如果没有什么都不用做

        info = dict()
        data = dict()
        info['statusCode'] = 200
        data['studentID'] = stu_id
        info['data'] = data
        sql = '''update seat_info set seat_status=1 where seat_info."user_id"=''' + (str(stu_id))
        cursor.execute(sql)

        sql = '''delete from seat_leave_briefly where (user_id=:user_id_toFeed)'''
        cursor.execute(sql, {'user_id_toFeed': stu_id})

        conn.commit()

        return jsonify(info)

    else:
        info = dict()
        info['statusCode'] = 400
        return jsonify(info)


'''
离开图书馆
'''
@app.route('/leaveLib', methods=['POST', 'GET'])
def leave_lib():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())

    stu_id = accept_data['studentID']

    sql = '''select seat_id from seat_info where (user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})
    seat_id = cursor.fetchall()
    seat_id = seat_id[0][0]
    # 假设所有图书馆内人员都出现在seat_info中
    info = dict()
    data = dict()
    data['seatID'] = seat_id
    info['data'] = data

    sql = '''select * from seat_leave_briefly where (user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})

    listexample = cursor.fetchall()

    if len(listexample) != 0:
        # 短暂离席表中有这个人
        info['statusCode'] = 200
    else:
        sql = '''update seat_info set seat_status=0 where (user_id=:user_id_toFeed)'''
        cursor.execute(sql, {'user_id_toFeed': stu_id})
        info['statusCode'] = 200
        # 这个人直接离席，返回200还是400？

    conn.commit()

    return jsonify(info)


'''
短暂离席
'''
@app.route('/seat/leave', methods=['POST', 'GET'])
def seat_leave():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    accept_data = json.loads(request.get_data())

    stu_id = accept_data['studentID']

    sql = '''select seat_id from seat_info where(user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})
    seat_id = cursor.fetchall()
    seat_id = seat_id[0][0]

    sql = '''insert into seat_leave_briefly
             (id, seat_id, user_id, leave_time)
             values
             (:id, :seat_id, :user_id, datetime('now', 'localtime'))'''
    cursor.execute(sql, {'id': 210, 'seat_id': seat_id, 'user_id': stu_id})

    sql = '''update seat_info set seat_status=2 where seat_info."user_id"='''+(str(stu_id))
    cursor.execute(sql)

    conn.commit()

    info = dict()
    data = dict()
    info['statusCode'] = 200
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

    sql = '''select seat_id, seat_status, seat_type, seat_row, seat_col
             from seat_info where (user_id=:user_id_toFeed)'''
    cursor.execute(sql, {'user_id_toFeed': stu_id})
    listexample = cursor.fetchall()

    if len(listexample) == 0:
        info['statusCode'] = 400    # seat_info中查无此人，暂时选择返回400：携带参数错误（建议修改返回码，或重新指定返回码规则）
    else:
        info['statusCode'] = 200    # seat_info中有此人座位记录，返回data中包括'user_id','seat_id','seat_status'
        select_seat_id, select_seat_status, select_seat_type, select_seat_row, select_seat_col = listexample[0]
        data = dict()
        data['studentID'] = stu_id
        seat_data = dict()
        seat_data['seatID'] = select_seat_id
        seat_data['seatStatus'] = select_seat_status
        seat_data['seatType'] = select_seat_type
        seat_data['seatRow'] = select_seat_row
        seat_data['seatCol'] = select_seat_col
        data['seat'] = seat_data
        info['data'] = data

    conn.commit()

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
    sql = '''select seat_type from seat_info where (seat_id=:seat_id_toFeed)'''
    cursor.execute(sql, {'seat_id_toFeed': seat_id})
    listexample = cursor.fetchall()

    if len(listexample) == 0 or listexample[0][0] == 0:
        info['statusCode'] = 400  # 查找失败（前端seat_id非法）或者seat_id所指座位标记为损坏，返回400
    else:
        info['statusCode'] = 200  # 查找成功
        sql = '''update seat_info set seat_status=1, user_id=:stu_id_toFeed where (seat_id=:seat_id_toFeed)'''
        cursor.execute(sql, {'stu_id_toFeed': stu_id, 'seat_id_toFeed': seat_id})

    data = dict()
    data['studentID'] = stu_id
    data['seatID'] = seat_id
    info['data'] = data

    conn.commit()

    return jsonify(info)


if __name__ == '__main__':
    app.run()