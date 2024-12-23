from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from functools import wraps

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Database Connection
def get_db_connection():
    if 'db_user' not in session or 'db_password' not in session:
        raise Exception("Database login credentials not found in session.")
    return mysql.connector.connect(
        host="localhost",
        user=session['db_user'],
        password=session['db_password'],
        database="panaderia"
    )


# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Храним параметры подключения в сессии
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            # Проверяем подключение к базе данных
            conn = mysql.connector.connect(
                host="localhost",
                user=username,
                password=password,
                database="panaderia"
            )
            conn.close()

            # Сохраняем данные подключения в сессии
            session['logged_in'] = True
            session['db_user'] = username
            session['db_password'] = password

            return redirect(url_for('insert_data'))
        except mysql.connector.Error as e:
            error = f"Error connecting to database: {str(e)}"
    return render_template('login.html', error=error)



@app.route('/insert_data', methods=['GET', 'POST'])
@login_required
def insert_data():
    table = request.args.get('table', None)
    conn = None
    cursor = None
    columns = []
    message = None
    inserted_data = None
    dropdown_options = {}
    required_columns = {}
    tables_data = {}
    edit_row_data = None  # Данные для редактирования
    primary_key_column = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем список таблиц
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        # Если таблица не выбрана или не существует, устанавливаем первую таблицу из списка
        if not table or table not in tables:
            table = tables[0] if tables else None

        if not table:
            message = "No tables available in the database."
            return render_template('insert_and_show_tables.html', 
                                   table=None, columns=[], tables=tables, 
                                   message=message)

        # Получаем структуру текущей таблицы
        cursor.execute(f"DESCRIBE {table}")
        table_structure = cursor.fetchall()

        for row in table_structure:
            column_name = row[0]
            column_type = row[1]
            is_nullable = row[2]

            columns.append(column_name)

            if row[3] == 'PRI':
                primary_key_column = column_name

            required_columns[column_name] = (is_nullable == 'NO')

            if column_type.startswith('set'):
                options = column_type.strip("set()").replace("'", "").split(",")
                dropdown_options[column_name] = [(option, option) for option in options]

        # Формируем данные для связанных таблиц
        for column in columns:
            if column.endswith('_id'):
                base_name = column[:-3]
                possible_tables = [base_name, base_name + 's', base_name + 'es']
                for related_table in possible_tables:
                    try:
                        cursor.execute(f"SHOW TABLES LIKE '{related_table}'")
                        if cursor.fetchone():
                            cursor.execute(f"DESCRIBE {related_table}")
                            related_structure = cursor.fetchall()
                            primary_key = next((col[0] for col in related_structure if col[3] == 'PRI'), None)
                            name_column = next((col[0] for col in related_structure if col[0].lower() == 'nombre'), None)
                            if primary_key and name_column:
                                cursor.execute(f"SELECT {primary_key}, {name_column} FROM {related_table}")
                                dropdown_options[column] = cursor.fetchall()
                            break
                    except Exception as e:
                        continue

        # Обработка POST-запроса для вставки или обновления
        if request.method == 'POST':
            if 'table' in request.form:
                selected_table = request.form['table']
                return redirect(url_for('insert_data', table=selected_table))

            try:
                data = request.form.to_dict()
                filtered_data = {key: value for key, value in data.items() if key in columns}

                action = request.form.get('action')
                if action == 'update' and primary_key_column in filtered_data:
                    row_id = filtered_data.pop(primary_key_column)
                    update_query = ', '.join([f"{col} = %s" for col in filtered_data.keys()])
                    query = f"UPDATE {table} SET {update_query} WHERE {primary_key_column} = %s"
                    cursor.execute(query, list(filtered_data.values()) + [row_id])
                    message = f"Row with {primary_key_column} {row_id} updated successfully!"
                elif action == 'insert':
                    query_columns = ', '.join(filtered_data.keys())
                    values = ', '.join(['%s'] * len(filtered_data))
                    query = f"INSERT INTO {table} ({query_columns}) VALUES ({values})"
                    cursor.execute(query, list(filtered_data.values()))
                    message = f"Data inserted into '{table}' successfully!"
                else:
                    message = "Invalid action or missing primary key for update."
                conn.commit()
            except Exception as e:
                message = f"An error occurred: {str(e)}"

        # Получаем данные всех таблиц для отображения
        for tbl in tables:
            cursor.execute(f"SELECT * FROM {tbl}")
            columns_in_table = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            tables_data[tbl] = {'columns': columns_in_table, 'rows': rows}

        # Обработка редактирования
        if 'edit_id' in request.args and primary_key_column:
            edit_id = request.args.get('edit_id')
            query = f"SELECT * FROM {table} WHERE {primary_key_column} = %s"
            cursor.execute(query, (edit_id,))
            edit_row_data = dict(zip(columns, cursor.fetchone()))

    except Exception as e:
        message = f"An error occurred: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'insert_and_show_tables.html',
        table=table,
        columns=columns,
        dropdown_options=dropdown_options,
        message=message,
        inserted_data=inserted_data,
        tables_data=tables_data,
        edit_row_data=edit_row_data,
        required_columns=required_columns,
        primary_key_column=primary_key_column,
        tables=tables
    )



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/delete_row/<table>/<row_id>', methods=['POST'])
@login_required
def delete_row(table, row_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Определяем первичный ключ таблицы
        cursor.execute(f"DESCRIBE {table}")
        table_structure = cursor.fetchall()
        primary_key_column = next((row[0] for row in table_structure if row[3] == 'PRI'), None)

        if primary_key_column:
            query = f"DELETE FROM {table} WHERE {primary_key_column} = %s"
            cursor.execute(query, (row_id,))
            conn.commit()

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('insert_data', table=table))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
