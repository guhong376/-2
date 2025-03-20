from models import SessionLocal
from models import House
import pandas as pd

def view_database():
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 查询所有房源信息
        houses = db.query(House).all()
        
        # 将查询结果转换为DataFrame
        data = []
        for house in houses:
            data.append({
                'ID': house.id,
                '标题': house.title,
                '地址': house.address,
                '户型': house.house_type,
                '面积': house.area,
                '朝向': house.direction,
                '关注信息': house.follow_info,
                '总价': house.total_price,
                '单价': house.unit_price,
                '创建时间': house.created_at
            })
        
        df = pd.DataFrame(data)
        
        # 打印基本信息
        print("\n数据库中的房源总数：", len(df))
        print("\n数据预览：")
        print(df.head())
        
        # 打印统计信息
        print("\n基本统计信息：")
        print(df.describe())
        
        # 保存到CSV文件
        df.to_csv('data/houses_query.csv', index=False, encoding='utf-8-sig')
        print("\n完整数据已保存到 data/houses_query.csv")
        
    finally:
        db.close()

if __name__ == '__main__':
    view_database() 