import vertica_python
import  os
import json
from functools import lru_cache


# 从环境变量获取连接信息
env_connection_info = os.environ.get('SQL_CONNECTION_STR')

if env_connection_info is not None:
    conn_info = json.loads(env_connection_info)
else:
    # 如果环境变量未设置，提供默认值
    conn_info = {
        'host': '10.159.6.12',
        'user': 'gpt',
        'password': '7ZB37Zj9ohN!al%Y',
        'database': 'quant'
    }

@lru_cache(maxsize=None)
def getDataDictionary() -> str:
    # 建立数据库连接
    connection = vertica_python.connect(**conn_info)

    try:
        # 创建游标
        cur = connection.cursor()
        
        # 查询 TEST.GPT_TABLE_dictionary 表
        cur.execute('SELECT SCHEMA_NAME,TABLE_NAME,TABLE_KEYWORDS FROM TEST.GPT_TABLE_dictionary')
        table_results = cur.fetchall()
        
        # 查询 TEST.GPT_FIELD_dictionary 表
        cur.execute('SELECT SCHEMA_NAME,TABLE_ENAME,FIELD_ENAME,FIELD_KEYWORDS FROM TEST.GPT_FIELD_dictionary')
        field_results = cur.fetchall()

        # 创建 JSON 格式
        result_json = {
            "tableSchemas": table_results,
            "fieldSchemas": field_results
        }

         # 将结果转换为 JSON 字符串
        result_json_str = json.dumps(result_json, indent=2)
    
        # 打印 JSON 格式数据
        print(result_json_str)

        return result_json_str

    finally:
        # 关闭连接
        connection.close()

def clearCache():
    getDataDictionary.cache_clear()