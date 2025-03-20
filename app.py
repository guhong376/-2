from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import pymysql
from config import DB_CONFIG
import time

app = Flask(__name__)

def get_db():
    """获取数据库连接"""
    try:
        print(f"尝试连接数据库: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, user={DB_CONFIG['user']}, database={DB_CONFIG['database']}")
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4'
        )
        print("数据库连接成功！")
        return conn
    except Exception as e:
        print(f"数据库连接错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        return None

# 缓存装饰器，缓存时间为5分钟
def cache_with_timeout(timeout=300):
    def decorator(func):
        cache = {}
        
        def wrapper(*args, **kwargs):
            now = time.time()
            cache_key = str(args) + str(kwargs)
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if now - timestamp < timeout:
                    return result
            
            result = func(*args, **kwargs)
            cache[cache_key] = (result, now)
            return result
        wrapper.__name__ = func.__name__  # 保持函数名称一致
        return wrapper
    return decorator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/price_by_area')
@cache_with_timeout()
def price_by_area():
    conn = get_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
        
    try:
        # 获取面积和价格数据
        query = """
            SELECT area, total_price 
            FROM houses 
            WHERE area IS NOT NULL 
            AND total_price IS NOT NULL 
            AND area > 0 
            AND total_price > 0
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return jsonify({'error': '没有数据'}), 404
            
        # 确保数据类型正确
        df['area'] = pd.to_numeric(df['area'], errors='coerce')
        df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce')
        
        # 移除异常值
        df = df.dropna()
        df = df[df['area'] <= df['area'].quantile(0.95)]  # 移除面积异常值
        df = df[df['total_price'] <= df['total_price'].quantile(0.95)]  # 移除价格异常值
        
        x = df['area'].tolist()
        y = df['total_price'].tolist()
        
        # 计算相关系数
        correlation = np.corrcoef(x, y)[0, 1]
        
        return jsonify({
            'x': x,
            'y': y,
            'correlation': float(correlation) if not np.isnan(correlation) else 0
        })
    except Exception as e:
        print(f"查询错误: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/price_by_direction')
@cache_with_timeout()
def price_by_direction():
    conn = get_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
        
    try:
        # 按朝向统计平均价格
        query = """
            SELECT direction, AVG(total_price) as avg_price
            FROM houses
            WHERE direction IS NOT NULL AND total_price IS NOT NULL
            GROUP BY direction
            ORDER BY avg_price DESC
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return jsonify({'error': '没有数据'}), 404
            
        directions = df['direction'].tolist()
        prices = df['avg_price'].tolist()
        
        return jsonify({
            'directions': directions,
            'prices': prices
        })
    except Exception as e:
        print(f"查询错误: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/price_by_house_type')
@cache_with_timeout()
def price_by_house_type():
    conn = get_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
        
    try:
        # 按户型统计平均价格
        query = """
            SELECT house_type, AVG(total_price) as avg_price
            FROM houses
            WHERE house_type IS NOT NULL AND total_price IS NOT NULL
            GROUP BY house_type
            ORDER BY avg_price DESC
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return jsonify({'error': '没有数据'}), 404
            
        types = df['house_type'].tolist()
        prices = df['avg_price'].tolist()
        
        return jsonify({
            'types': types,
            'prices': prices
        })
    except Exception as e:
        print(f"查询错误: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/price_distribution')
@cache_with_timeout()
def price_distribution():
    conn = get_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
        
    try:
        # 获取价格分布数据
        query = """
            SELECT total_price
            FROM houses
            WHERE total_price IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return jsonify({'error': '没有数据'}), 404
            
        prices = df['total_price'].tolist()
        
        # 计算价格区间
        bins = np.linspace(min(prices), max(prices), 10)
        hist, _ = np.histogram(prices, bins=bins)
        
        return jsonify({
            'bins': bins.tolist(),
            'counts': hist.tolist()
        })
    except Exception as e:
        print(f"查询错误: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/metro_analysis')
@cache_with_timeout()
def metro_analysis():
    conn = get_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
        
    try:
        # 分析地铁对价格的影响
        query = """
            SELECT title, total_price
            FROM houses
            WHERE total_price IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return jsonify({'error': '没有数据'}), 404
            
        # 判断是否靠近地铁
        df['has_metro'] = df['title'].str.contains('地铁', na=False)
        
        # 计算靠近地铁和不靠近地铁的平均价格
        metro_prices = df[df['has_metro']]['total_price'].tolist()
        non_metro_prices = df[~df['has_metro']]['total_price'].tolist()
        
        return jsonify({
            'metro_avg': float(np.mean(metro_prices)) if metro_prices else 0,
            'non_metro_avg': float(np.mean(non_metro_prices)) if non_metro_prices else 0,
            'metro_count': len(metro_prices),
            'non_metro_count': len(non_metro_prices)
        })
    except Exception as e:
        print(f"查询错误: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 