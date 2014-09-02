
from z9.mapex import MySqlClient, Pool

production = Pool(MySqlClient, ("localhost", 3306, "root", "password", "{default}"))
beta = Pool(MySqlClient, ("localhost", 3306, "root", "password", "{default}"))
unittests = Pool(MySqlClient, ("localhost", 3306, "root", "password", "{default}"))