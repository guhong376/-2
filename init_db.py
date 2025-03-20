import pymysql
from config import DB_CONFIG

def init_database():
    # 首先创建数据库连接（不指定数据库）
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    
    try:
        with conn.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 {DB_CONFIG['database']} 创建成功")
            
            # 使用数据库
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # 创建表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS houses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200),
                    address VARCHAR(200),
                    house_type VARCHAR(50),
                    area FLOAT,
                    direction VARCHAR(50),
                    follow_info VARCHAR(100),
                    total_price FLOAT,
                    unit_price FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_area_price (area, total_price),
                    INDEX idx_direction (direction),
                    INDEX idx_house_type (house_type),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("表 houses 创建成功")
            
        conn.commit()
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 