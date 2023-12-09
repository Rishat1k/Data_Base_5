import psycopg2


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS clients(
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(80) NOT NULL,
                        last_name VARCHAR(80) NOT NULL,
                        email VARCHAR(80) NOT NULL UNIQUE
                        );
                        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS phone_numbers(
                            id SERIAL PRIMARY KEY,
                            client_id INTEGER NOT NULL REFERENCES clients(id),
                            number VARCHAR(12)
                            );
                            """)
        conn.commit()


def add_client(conn, first_name, last_name, email, number=None):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO clients(first_name, last_name, email)
                        VALUES(%s, %s, %s)
                        RETURNING id;""", (first_name, last_name, email))
        if number:
            cur.execute("""INSERT INTO phone_numbers(client_id, number)
                            VALUES(%s, %s);""", (cur.fetchone()[0], number))
        conn.commit()


def add_phone(conn, client_id, number):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO phone_numbers(client_id, number)
                        Values(%s, %s);""", (client_id, number))
        conn.commit()


def change_client(conn, id, first_name=None, last_name=None, email=None, number=None):
    with conn.cursor() as cur:
        if first_name is None:
            cur.execute("""SELECT first_name FROM clients
                            WHERE id = %s;""", (id,))
            first_name = cur.fetchone()[0]

        if last_name is None:
            cur.execute("""SELECT last_name FROM clients
                            WHERE id = %s;""", (id,))
            last_name = cur.fetchone()[0]

        if email is None:
            cur.execute("""SELECT email FROM clients
                            WHERE id = %s;""", (id,))
            email = cur.fetchone()[0]

        cur.execute("""UPDATE clients
                        SET first_name = %s, last_name = %s, email = %s
                        WHERE id = %s;""", (first_name, last_name, email, id))

        if number:
            cur.execute("""UPDATE phone_numbers
                            SET number = %s
                            WHERE client_id = %s;""", (number, id))
        conn.commit()


def delete_phone(conn, client_id, number):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phone_numbers
                        WHERE client_id = %s AND number = %s;""", (client_id, number))
        conn.commit()


def delete_client(conn, id):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phone_numbers
                        WHERE client_id = %s;""", (id,))
        cur.execute("""DELETE FROM clients
                        WHERE id = %s;""", (id,))
        conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, number=None):
    with conn.cursor() as cur:
        cur.execute("""SELECT first_name, last_name, email, number FROM clients, phone_numbers
                        WHERE first_name = %s OR last_name = %s OR email = %s OR number = %s;""", (first_name, last_name, email, number))
        print(cur.fetchone())


database = ''
user = ''
password = ''


with psycopg2.connect(database=database, user=user, password=password) as conn:
    create_table(conn)
    add_client(conn, 'Andrey', 'Romanov', '123@yandex.ru')
    add_client(conn, 'Max', 'Levin', 'www@mail.ru', '89998887777')
    add_phone(conn, 1, '89989988999')
    add_phone(conn, 2, '89015031722')
    change_client(conn, 2, first_name='Maxim', email='www@gmail.com')
    delete_phone(conn, 2, '89998887777')
    delete_client(conn, 1)
    find_client(conn, first_name='Maxim')
conn.close()
