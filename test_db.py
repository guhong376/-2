import pymysql
from config import DB_CONFIG

def test_connection():
    try:
        # 创建数据库连接
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        
        # 创建游标对象
        cursor = conn.cursor()
        
        # 执行查询
        cursor.execute("SELECT COUNT(*) FROM houses")
        count = cursor.fetchone()[0]
        print(f"数据库中的房源总数：{count}")
        
        # 获取表结构
        cursor.execute("DESCRIBE houses")
        table_info = cursor.fetchall()
        print("\n表结构：")
        for field in table_info:
            print(field)
        
        # 获取部分数据
        cursor.execute("SELECT * FROM houses LIMIT 5")
        rows = cursor.fetchall()
        print("\n数据预览：")
        for row in rows:
            print(row)
            
    except Exception as e:
        print(f"连接数据库时出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_connection() 