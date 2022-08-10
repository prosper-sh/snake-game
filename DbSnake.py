
import sqlite3
from DataConfig import Config, grid
from os import system
from Snake import Snake
from Util import Util

class DbSnake :

    def __init__(self) :
        self.path = Config.get('db-snake-path')
        self.conn = None
        self.db_exists = bool(Config.get('db-snake-exists'))
        self.is_conn = False # Not connected yet

    def createDb(self) :
        if self.db_exists :
            return                                              #The database already exists
        Config.change('db-snake-exists', 1)
        #Config.update()                                        #Save change in configuration file
        script = self.loadscript(Config.get('script-path'))
        self._connect_if_is_not_connected()
        self.conn.executescript(script)

    def connect(self) :
        try :
            convert_snake = Util.to_snake
            adapt_snake = Util.from_snake
            sqlite3.register_adapter(Snake, adapt_snake)
            sqlite3.register_converter("Snake", convert_snake)
            self.conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
            self.is_conn = True
        except sqlite3.Error as e :
            raise DbScoreError("Could Not Connect To : " + self.path + "\n")


    def _connect_if_is_not_connected(self) :
        if self.is_conn :
            return
        self.connect()

    def loadscript(self, path):
        #Read the second table
        with open(path) as f :
            return f.read().split(';')[1] + ';'

    def insert(self, snake) :
        self._connect_if_is_not_connected()
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO snake VALUES(?, DATE())', (snake,))
        cursor.close()
        self.conn.commit()

    def get(self) :
        self._connect_if_is_not_connected()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM snake')
        self.conn.commit()
        return cursor.fetchall()

    def rmDb(self) :
        #Remove database file (table)
        if self.db_exists :
            Config.change('db-snake-exists', 0)
            #Config.update()
            self.db_exists = self.is_conn = False
            system('rm data/snake.db')
            system('touch data/snake.db')

    def delete(self) :
        self._connect_if_is_not_connected()
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM snake')
        self.conn.commit()
        cursor.close()

    def is_connected(self) :
        return self.is_conn

    def close(self) :
        if self.is_conn :
            self.conn.close()
            self.is_conn = False



#-------------------------------------
#---             Test             ----
#-------------------------------------

if __name__ == '__main__' :
    from time import sleep
    is_saved = False
    def SaveSnake() :
        global is_saved
        from DbSnake import DbSnake
        db = DbSnake()
        db.rmDb()
        db.createDb()
        snake = Snake(direction='up')
        nb = 0
        while nb < 7 :
            if snake.is_dead() :
                system('clear')
                print('Snake is dead\n')
                break
            grid.desc(snake)
            snake.move()
            if nb == 4 :
                snake.move('left')

            sleep(.7)
            system('clear')
            nb += 1

        db.insert(snake)
        is_saved = True
        db.close()
        Config.update_change()

    def loadSnake() :
        from DbSnake import DbSnake
        db = DbSnake()
        db.connect()
        snake = db.get()[0][0]
        n = 0
        while True :
            if snake.is_dead() :
                system('clear')
                print('Snake is dead\n')
                break
            n += 1
            if n == 3 :
                snake.move('down')
            grid.desc(snake)
            snake.move()
            sleep(.7)
            system('clear')

        db.close()

    SaveSnake()
    if is_saved :
        loadSnake()


