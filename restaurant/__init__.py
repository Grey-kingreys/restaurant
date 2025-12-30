import pymysql

# Forcer PyMySQL à s'installer comme MySQLdb
pymysql.install_as_MySQLdb()

# Contourner la vérification de version
pymysql.version_info = (2, 2, 1, "final", 0)