from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QPushButton
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from Algorithm.libs.logger.log import get_logger
import Algorithm.libs.config.model_cfgs as cfgs

log_info = get_logger(__name__)
ISLOG=cfgs.ISLOG

def init_db(db_path, db_name):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_path)
    if not db.open():
        print("Error: Unable to open database")

        if ISLOG:
            log_info.error("{}_{} Unable to open database.".format(db_path, db_name))
        return False
    query = QSqlQuery()
    query.exec_("CREATE TABLE IF NOT EXISTS {} (id integer primary key, name text, category varchar, box text, feat text, image varchar)".format(db_name))
    return True

def check(func, *args):
    if not func(*args):
        raise ValueError(func.__self__.lastError())

def load_sql_feat_info(db_path, db_name):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_path)
    if not db.open():
        print("Error: Unable to open database")
        if ISLOG:
            log_info.error("{}_{} Unable to open database.".format(db_path, db_name))
        return False

    query = QSqlQuery()
    query.exec("SELECT name, feat FROM {}".format(db_name))
    feat_list = []
    label_list = []
    if not query.isActive():
        if ISLOG:
            log_info.error("{}_{} query feature error.".format(db_path, db_name))
        print("Error:", query.lastError().text())
    else:
        results = []
        while query.next():
            # 通过列索引检索数据
            data1 = query.value(0)  # 第一列的值
            data2 = query.value(1)  # 第二列的值
            label_list.append(data1)
            feat_list.append(list(map(float,data2.split(','))))
    return feat_list, label_list

def _add_register(db_path, db_name, name, category, box, feat, image):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_path)
    if not db.open():
        print("Error: Unable to open database")
        if ISLOG:
            log_info.error("{}_{} Unable to open database.".format(db_path, db_name))
        return False
    q = QSqlQuery()
    INSERT_BOOK_SQL = "insert into {}(name, category, box, feat, image) values(?, ?, ?, ?, ?)".format(db_name)
    check(q.prepare, INSERT_BOOK_SQL)
    q.addBindValue(name)
    q.addBindValue(category)
    q.addBindValue(box)
    q.addBindValue(feat)
    q.addBindValue(image)
    q.exec()
    if q.lastError().isValid():
        # 查询执行失败，输出错误信息
        print("Error:", q.lastError().text())
    else:
        # 查询执行成功
        print("Query executed successfully")
