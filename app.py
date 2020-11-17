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

if __name__ == '__main__':
    app.run()