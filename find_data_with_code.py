import pandas as pd
from connect_to_code_interpretator import get_certain_data_from_file
import time
from config import PARQUET_DIR

def get_data_with_code(user_request, code):
    # time0 = time.perf_counter()
    file_path = PARQUET_DIR / f"{code}.parquet"
    # data = []
    # with open(file_path, 'r', encoding='utf-8') as f:
    #     for line in f:
    #         data.append(json.loads(line))
    # res=[]
    # years = [j for j in range(start_year, end_year+1)]
    # for i in data:
    #     if int(i['year']) in years:
    #         res.append(i)
    
    # # Теперь data — это список словарей
    
    # print(res)
    # res = []
    df = pd.read_parquet(file_path)
    # print('TIME -', time.perf_counter() - time0)
    time1 = time.perf_counter()
    data_answer = get_certain_data_from_file(user_request, code)
    # print('TIME -', time.perf_counter() - time1)

    # for i in df.values():
    # print('-------', df.shape)
    # print(df['column00'])
    # print(df.values.tolist()[:2])
    return [code, data_answer]
#     # print(df.head())
#     # print(df.columns)

# code = "40579"
# get_data_with_code(code,2005,2007)
