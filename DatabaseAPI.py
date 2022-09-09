import sqlite3

path_to_db = "Database\main.db"

class Quote():
    def __init__(self, creator: str, name: str, content: float):
        self.name = name
        self.content = content
        self.creator = creator

class Database(object):
    _instance = None

    def __init__(self) -> Exception:
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print("Creating Database Instance")
            cls._instance = cls.__new__(cls)

        return cls._instance
 
    def CreateUserIfNotExist(self, user:int) -> None:
        try:
            conn = sqlite3.connect(path_to_db)
            cursor = conn.cursor()
            query = f"""SELECT UID FROM Users WHERE UID = {user};"""
            cursor.execute(query)
            exists = cursor.fetchone()

            if exists:
                return
            else:
                createQuery = f"""INSERT INTO Users(UID) VALUES({user});"""
                cursor.execute(createQuery)
                conn.commit()

        except Exception as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def QuoteAlreadyExists(self, getOption:str, value:str) -> bool:
        return self.GetQuoteBy(getOption, value)

    def GetQuoteBy(self, getOption: str, value: str) -> Quote or None or list:
        quote = None
        if getOption.lower() == "name":
            try:
                con = sqlite3.connect(path_to_db)
                cur = con.cursor()
                value = value.lower()
                query = f"""
                SELECT *
                FROM Quotes
                WHERE Name LIKE '%%{value}%%';
                    """
                cur.execute(query)
                found = cur.fetchone()
                if found:
                    quote = Quote(found[0], found[1], found[2])
            except Exception as e:
                print(e)

        elif getOption.lower() == "content":
            try:
                con = sqlite3.connect(path_to_db)
                cur = con.cursor()
                value = value.lower()
                query = f"""
                SELECT *
                FROM Quotes
                WHERE Content LIKE '%%{value}%%';
                """
                cur.execute(query)
                found = cur.fetchall()
                if found:
                    quoteList = []
                    for quoteFound in found:
                        quoteList.append(Quote(quoteFound[0], quoteFound[1], quoteFound[2]))
                    quote = quoteList
            except Exception as e:
                print(e)

        elif getOption.lower() == "uid":
            try:
                con = sqlite3.connect(path_to_db)
                cur = con.cursor()
                value = int(value)
                query = f"""
                SELECT *
                FROM Quotes
                WHERE Author LIKE '%%{value}%%';
                """
                cur.execute(query)
                found = cur.fetchall()
                quoteList = []
                for quoteFound in found:
                    quoteList.append(Quote(quoteFound[0], quoteFound[1], quoteFound[2]))
                quote = quoteList
            except Exception as e:
                print(e)

        cur.close()
        con.close()
        return quote

    def CreateQuote(self, author:int, name:str, content:str) -> bool:
        quoteCommitSuccess = False
        existsA = self.QuoteAlreadyExists("name", name)
        existsB = self.QuoteAlreadyExists("content", content)
        if existsA or existsB :
                return False
        try:
            self.CreateUserIfNotExist(author)
            conn = sqlite3.connect(path_to_db)
            cur = conn.cursor()
            validationQuery = f"""SELECT UID FROM Blacklist WHERE UID = {author};"""
            cur.execute(validationQuery)
            isBlacklisted = cur.fetchone()
            if isBlacklisted == None:
                quoteQuery = f'INSERT INTO Quotes(Author, Name, Content) VALUES({author}, "{name.lower()}", "{content}");'
                cur.execute(quoteQuery)
                conn.commit()
                quoteCommitSuccess = True

        except Exception as e:
            print(e)
        finally:
            cur.close()
            conn.close()
            return quoteCommitSuccess

    def RemoveQuoteBy(self, getOption: str, value:str) -> bool:
        success = False
        if getOption.lower() == "name":
            try:
                conn = sqlite3.connect(path_to_db)
                cur = conn.cursor()
                query = f"""
                DELETE FROM Quotes WHERE Name = '{value.lower()}';
                """
                cur.execute(query)
                conn.commit()
                success = True
            except Exception as e:
                print(e)
            finally:
                cur.close()
                conn.close()
                return success
        elif getOption.lower() == "content":
            try:
                conn = sqlite3.connect(path_to_db)
                cur = conn.cursor()
                query = f"""
                DELETE FROM Quotes WHERE Content LIKE '%{value.lower()}%';
                """
                cur.execute(query)
                conn.commit()
                success = True
            except Exception as e:
                print(e)
            finally:
                cur.close()
                conn.close()
                return success
        elif getOption.lower() == "uid":
            try:
                conn = sqlite3.connect(path_to_db)
                cur = conn.cursor()
                value = int(value)
                query = f"""
                DELETE FROM Quotes WHERE Author = '{value}';
                """
                cur.execute(query)
                conn.commit()
                success = True
            except Exception as e:
                print(e)
            finally:
                cur.close()
                conn.close()
                return success

    def AddBlacklist(self, user:int, adminID:int, reason:str = "None Given") -> bool:
        blacklisted = False
        try:
            self.CreateUserIfNotExist(user)
            self.CreateUserIfNotExist(adminID)
            conn = sqlite3.connect(path_to_db)
            cursor = conn.cursor()
            blacklistQuery = f"""
            INSERT INTO Blacklist(UID, Reason, AdminID) VALUES({user},'{reason}',{adminID})
            """
            cursor.execute(blacklistQuery)
            conn.commit()
            blacklisted = True

        except Exception as e:
            print(e+"\n Unexpected Error in AddBlacklist")
            
        finally:
            cursor.close()
            conn.close()
            return blacklisted

    def RemoveBlacklist(self, user:int) -> bool:
        removed = False
        try:
            conn = sqlite3.connect(path_to_db)
            cursor = conn.cursor()
            query = f"DELETE FROM Blacklist WHERE UID = {user}"
            cursor.execute(query)
            conn.commit()
            removed = True

        except Exception as e:
            print(e)

        finally:
            cursor.close()
            conn.close()
            return removed