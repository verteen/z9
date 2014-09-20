
from mapex import SqlMapper


class AccountsMapper(SqlMapper):
    """ Маппер аккаунтов """

    def bind(self):
        """ Настраиваем маппинг """
        from z9.core.auth.models import Accounts, Account
        from z9.core.auth.exceptions import DublicateLogin

        AccountsMapper.dublicate_record_exception = DublicateLogin

        self.set_new_item(Account)
        self.set_new_collection(Accounts)
        self.set_collection_name("Accounts")
        self.set_map([
            self.str("login", "Login"),
            self.str("password_raw", "Password"),
            self.str("token", "Token"),
        ])

    @classmethod
    def up(cls):
        cls.pool.db.execute_raw(
            """
            CREATE TABLE `Accounts` (
              `Login` varchar(255) NOT NULL,
              `Password` varchar(32) NOT NULL,
              `Token` varchar(32) DEFAULT NULL,
              PRIMARY KEY (`Login`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """
        )

    @classmethod
    def down(cls):
        cls.pool.db.execute_raw(
            """DROP TABLE IF EXISTS `Accounts`;"""
        )

