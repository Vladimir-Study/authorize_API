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
                    'status_2': line_table[12],
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
        parser.add_argument("client_secret_performance", type=str)
        parser.add_argument("client_id", type=int, required=True)
        parser.add_argument("client_id_performance", type=str)
        parser.add_argument("client_id_api", type=str)
        parser.add_argument("api_key", type=str)
        parser.add_argument("campaigns_id", type=str)
        parser.add_argument("name", type=str, required=True)
        parser.add_argument("yandex_url", type=str)
        parser.add_argument("internal_token", type=str)
        add_params = parser.parse_args()
        conn = connections()
        with conn:
            with conn.cursor() as cursor:
                for key, val in add_params.items():
                    if val is None:
                        add_params[key] = 'null'
                cursor.execute(
                        f"INSERT INTO account_list (mp_id, client_secret_performance, "
                        f"client_id, client_id_performance, client_id_api, "
                        f"api_key, campaigns_id, name, yandex_url, internal_token) "
                        f"VALUES ({add_params['mp_id']}, "
                        f"'{add_params['client_secret_performance']}', {add_params['client_id']}, "
                        f"'{add_params['client_id_performance']}', '{add_params['client_id_api']}', "
                        f"'{add_params['api_key']}', '{add_params['campaigns_id']}', '{add_params['name']}', "
                        f"'{add_params['yandex_url']}', '{add_params['internal_token']}')"
                )
                conn.commit()
        return add_params


class EditUser(Resource):

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=int, required=True)
        parser.add_argument("mp_id", type=int)
        parser.add_argument("client_secret_performance", type=str)
        parser.add_argument("client_id", type=int, required=True)
        parser.add_argument("client_id_performance", type=str)
        parser.add_argument("client_id_api", type=str)
        parser.add_argument("api_key", type=str)
        parser.add_argument("campaigns_id", type=str)
        parser.add_argument("name", type=str)
        parser.add_argument("yandex_url", type=str)
        parser.add_argument("internal_token", type=str)
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
                        f"client_secret_performance = '{edit_params['client_secret_performance']}', "
                        f"client_id = {edit_params['client_id']}, client_id_performance = "
                        f"'{edit_params['client_id_performance']}', client_id_api = '{edit_params['client_id_api']}', "
                        f"api_key = '{edit_params['api_key']}', campaigns_id = '{edit_params['campaigns_id']}', "
                        f"name = '{edit_params['name']}', yandex_url = '{edit_params['yandex_url']}', "
                        f"internal_token = '{edit_params['internal_token']}' WHERE id = {edit_params['id']}"
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
    app.run(debug=True, port=5000, host="127.0.0.1")
    #pass
