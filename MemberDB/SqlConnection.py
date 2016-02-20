import MySQLdb
import logging

class SqlConnection:
    '''
    Class to set up and employ an SQL connection.
    '''
    
    def __init__(self, host, database, username, password, loggingFacility):
        '''
        (SqlConnection, str, str, str) -> None
        
        Takes all the credentials to start an SQL connection and creates the connection object.
        '''
        self.db = MySQLdb.connect(host, username, password, database)
        self._connection = self.db.cursor()
        self._username = username
        self._database = database
        self._logger = loggingFacility

    def __str__(self):
        '''
        (SqlConnection) -> str
        
        Returns a human-readable representation of the connection that includes the username used to connect and the database where we work.
        '''
        return self._username + " @ " + self._database
           
    def dosql(self, sql, value, expectRows, dryrun=False):
        '''
        (SqlConnection, str, tuple, bool, bool) -> list (or None)
        
        Executes the SQL query in sql, including the tuple value. The values in the tuple value are set in place of the placeholders in sql. The placeholders should correspond to the types in the tuple value, e.g. %s should be used to insert an str. To not pass values, pass an empty string. If expectRows is True, the rows are fetched with fetchall() and returned to the caller as a list of lists. Otherwise, the function returns None. dryrun specifies whether we are in a debugging scenario: if it is True, queries are logged but not executed. None is returned whenever dryrun is True. 
        
        Examples:
        
        > instance.dosql("INSERT INTO table (firstname, lastname) VALUES (%s, %s)", ("John", "Doe"), False)
        None
        > instance.dosql("SELECT * FROM table", "", True)
        [['John', 'Doe']]
        > instance.dosql("SELECT * FROM complex INNER JOIN query", "", True, True)
        None
        '''
        if value != "":
            self._logger.debug((sql % value).encode("utf-8"))
        else:
            self._logger.debug(sql.encode("utf-8"))
        if not dryrun:
            try:
                if value != "":
                    self._connection.execute(sql, value)
                else:
                    self._connection.execute(sql)
                self.db.commit()
            except:
                self._logger.error("Error executing previous query")
        for msg in self._connection.messages:
            self._logger.debug(msg)
        if expectRows:
            return self._connection.fetchall()