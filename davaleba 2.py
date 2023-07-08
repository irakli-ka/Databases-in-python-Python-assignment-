import sqlite3
import texttable
import random


class AnimeDatabase:
    table = texttable.Texttable()

    def __init__(self, dbname):
        self._dbname = dbname
        self._con = None
        self._cur = None

    def connect(self):
        self._con = sqlite3.connect(self._dbname)
        self._cur = self._con.cursor()

    def disconnect(self):
        self._cur.close()
        self._con.close()

    def draw_table(self, res):
        self.table.header(["ID", "Name", "Sport", "Finished Airing", "Rating", "Seen"])
        self.table.set_cols_dtype(['i', 't', 't', 'i', 'f', 'i'])

        for row_id, name, sport, finished_airing, rating, seen in res:
            self.table.add_row([row_id, name, sport, finished_airing, rating, seen])

        self._cur.row_factory = lambda cursor, row: row[0]
        list_of_name_col = self._cur.execute("select name from animedb").fetchall()
        list_of_sport_col = self._cur.execute("select sport from animedb").fetchall()
        self._cur.row_factory = None

        name_length_values = []
        for item in list_of_name_col:
            if len(item) >= 4:
                name_length_values.append(len(item))

        sport_length_values = []
        for item in list_of_sport_col:
            if len(item) >= 5:
                sport_length_values.append(len(item))

        if name_length_values != [] and sport_length_values != []:
            self.table.set_cols_width([3, max(name_length_values), max(sport_length_values), 15, 6, 4])
        else:
            self.table.set_cols_width([3, 4, 5, 15, 6, 4])
        print(self.table.draw())
        self.table.reset()

    def create_table(self):
        self._cur.execute("""
            create table if not exists animedb
            (row_id integer primary key autoincrement,
            name text,
            sport text,
            finished_airing integer,
            rating real,
            seen integer)""")

    def insert_row(self, name, sport, finished_airing, rating, seen=0):
        self._cur.execute("""
            insert into animedb (name, sport, finished_airing, rating, seen)
            values (?, ?, ?, ?, ?)""", (name, sport, finished_airing, rating, seen))
        self._con.commit()

    def delete_row(self, row_id):
        self._cur.execute("""
            delete from animedb
            where row_id = ?""", (row_id,))
        self._con.commit()

    def mark_as_seen(self, row_id):
        self._cur.execute("""
            update animedb set seen = 1
            where row_id = ?""", (row_id,))
        self._con.commit()

    def select_all(self):
        res = self._cur.execute("select * from animedb")
        self.draw_table(res)

    def select_by_sport(self, sport):
        res = self._cur.execute("select * from animedb where sport = :sport", {"sport": sport})
        self.draw_table(res)

    def select_random(self):
        self._cur.row_factory = lambda cursor, row: row[0]
        suitable_ids_list = self._cur.execute("select row_id from animedb where seen = 0 and finished_airing = 1"). \
            fetchall()
        self._cur.row_factory = None
        suitable_num = len(suitable_ids_list)

        if suitable_num > 0:
            rand_id = random.choice(suitable_ids_list)
            res = self._cur.execute(
                """select row_id, name, sport, finished_airing, rating, seen from animedb where seen = 0 
                and finished_airing = 1 and row_id = :rand_id""", {"rand_id": rand_id})
            self.draw_table(res)
        else:
            print("\nAn anime that has finished airing and is not seen by you could not be found\n")


def main():
    database = AnimeDatabase("animedb.sqlite")
    database.connect()
    database.create_table()

    while True:
        print(
            "Choose an action:\n"
            "1. Add anime\n"
            "2. View all animes\n"
            "3. Filter animes by sport\n"
            "4. Choose random anime to watch\n"
            "5. Mark anime as seen\n"
            "6. Delete anime\n"
            "7. Quit"
        )
        user = input("Enter your choice: ")

        if user == "1":
            name = input("Enter name: ")
            sport = input("Enter type of sport: ").lower()
            finished_airing = input("Is the anime finished? [y/n]: ")
            if finished_airing == "y":
                finished_airing = 1
            else:
                finished_airing = 0
            rating = float(input("Enter rating: "))

            database.insert_row(name, sport, finished_airing, rating)

        elif user == "2":
            database.select_all()

        elif user == "3":
            database.select_by_sport((input("Enter type of sport: ").lower()))

        elif user == "4":
            database.select_random()

        elif user == "5":
            database.mark_as_seen(int(input("Enter ID: ")))

        elif user == "6":
            database.delete_row(int(input("Enter ID: ")))

        elif user == "7":
            database.disconnect()
            break


main()
