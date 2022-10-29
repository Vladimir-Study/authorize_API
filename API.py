import json
from pprint import pprint
from flask import Flask
from flask_restful import Api, Resource, reqparse
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()


def connections():
    conn = psycopg2.connect(
        host='rc1b-itt1uqz8cxhs0c3d.mdb.yandexcloud.net',
        port='6432',
        dbname='market_db',
        user=os.environ['DB_LOGIN'],
        password=os.environ['DB_PASSWORD'],
        target_session_attrs='read-write',
        sslmode='verify-full'
    )
    return conn


app = Flask(__name__)
api = Api(app)

param_desk = {}


class UsersStatus(Resource):

    def get(self, id):
        try:
            conn = connections()
            with conn:
                with conn.cursor() as select:
                    select.execute(f"SELECT * FROM account_list WHERE id = {id};")
                    line_table = select.fetchone()
            if line_table is not None:
                return {
                    'id': id,
                    'status_1': line_table[9],
                }
            return {
                'id': 'Not found'
            }
        except Exception as e:
            return {
                'Exception': e,
            }


class AddUser(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("mp_id", type=int, required=True)
        parser.add_argument("client_id", type=int, required=True)
        parser.add_argument("name", type=str, required=True)
        add_params = parser.parse_args()
        conn = connections()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                        f"INSERT INTO account_list (mp_id, "
                        f"client_id, name, status_1) "
                        f"VALUES ({add_params['mp_id']}, "
                        f"{add_params['client_id']}, '{add_params['name']}', 'Active')"
                )
                conn.commit()
        return add_params


class EditUser(Resource):

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=int, required=True)
        parser.add_argument("mp_id", type=int)
        parser.add_argument("client_id", type=int, required=True)
        parser.add_argument("name", type=str)
        edit_params = parser.parse_args()
        conn = connections()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM account_list WHERE id = {edit_params['id']}")
                line_table = cursor.fetchone()
                if line_table is None:
                    return {'Error': 'record with the same \'id\' missing'}
                else:
                    for key, val in edit_params.items():
                        if val is None:
                            edit_params[key] = 'null'
                    cursor.execute(
                        f"UPDATE account_list SET mp_id = {edit_params['mp_id']}, "
                        f"client_id = {edit_params['client_id']}, "
                        f"name = '{edit_params['name']}', status_1 = 'Active' "
                        f"WHERE id = {edit_params['id']}"
                    )
                    conn.commit()
        return edit_params


class DeleteAccount(Resource):

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        delete_line = parser.parse_args()
        conn = connections()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM account_list WHERE id = {delete_line['id']};")
                conn.commit()
        return {f"id: {delete_line['id']}": 'DELETE'}


api.add_resource(UsersStatus, '/account/status/<int:id>')
api.add_resource(AddUser, '/account/add')
api.add_resource(EditUser, '/account/edit')
api.add_resource(DeleteAccount, '/account/delete')


if __name__ == '__main__':
    app.run(debug=True, port=4000, host="127.0.0.1")
    #pass
