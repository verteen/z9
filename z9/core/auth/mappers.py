
from mapex import SqlMapper


class AccountsMapper(SqlMapper):
    """ Маппер аккаунтов """

    def bind(self):
        """ Настраиваем маппинг """
        from z9.core.auth.models import Accounts, Account, AccountSettings
        from z9.core.auth.exceptions import DublicateLogin

        AccountsMapper.dublicate_record_exception = DublicateLogin

        self.set_new_item(Account)
        self.set_new_collection(Accounts)
        self.set_collection_name("Accounts")
        self.set_map([
            self.str("login", "Login"),
            self.str("password_raw", "Password"),
            self.str("token", "Token"),
            self.embedded_list("settings_raw", AccountSettings)
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


class AccountSettingsMapper(SqlMapper):
    dependencies = [AccountsMapper]

    def bind(self):
        """ Настраиваем маппинг """
        from z9.core.auth.models import AccountSetting, AccountSettings, Accounts
        self.set_new_item(AccountSetting)
        self.set_new_collection(AccountSettings)
        self.set_collection_name("AccountSettings")
        self.set_map([
            self.int("id", "ID"),
            self.link("account", "Login", collection=Accounts),
            self.str("name", "Name"),
            self.str("value", "Value"),
        ])

    @classmethod
    def up(cls):
        cls.pool.db.execute_raw(
            """
            CREATE TABLE `AccountSettings` (
                `ID` INT(11) NOT NULL AUTO_INCREMENT,
                `Login` VARCHAR(255) NOT NULL,
                `Name` VARCHAR(255) NOT NULL,
                `Value` VARCHAR(255) NULL DEFAULT NULL,
                PRIMARY KEY (`ID`),
                INDEX `Login` (`Login`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """
        )

    @classmethod
    def down(cls):
        cls.pool.db.execute_raw(
            """DROP TABLE IF EXISTS `AccountSettings`;"""
        )
