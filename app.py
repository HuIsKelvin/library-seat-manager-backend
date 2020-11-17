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

    # accept_data = json.loads(request.get_data())
    #
    # stu_id = accept_data['studentID']
    stu_id = 3

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
    print(listexample)

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

    # accept_data = json.loads(request.get_data())
    #
    # stu_id = accept_data['studentID']
    stu_id = 4
    sql = '''select seat_id from seat_info where(user_id=:user_id)'''
    cursor.execute(sql, {'user_id': stu_id})
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


if __name__ == '__main__':
    app.run()