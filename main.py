import re
from create_json import requet_to_json_pydantic
from search_top_k import search
from ask_llm_for_data import is_requared_data
from final_llm_answer import get_final_llm_answer
from find_data_with_code import get_data_with_code
from checking_full_json import check_full_request
from config import PARQUET_DIR
# import time

# start_time = time.perf_counter()

user_request = input('Введите запрос: ')
# user_request = 'самая быстро растущая страна по числености в европе в период с 2015-2019 года'
# user_request = 'ВВП России за 2002 год в отношении к ВВП США'

temp0 = check_full_request(user_request)
while not temp0[0]:
    print(temp0[1])
    # time.sleep(0.5)
    temp0 = check_full_request(input('Введите запрос: '))

json_request = requet_to_json_pydantic(user_request)
# print(json_request)


finded_data = search(json_request['semantic_query'], 1)
code = finded_data[0][0]
# time2 = time.perf_counter()
# print('TIME -', time2 - start_time)
temp2 = get_data_with_code(user_request, code)
codes_data = [temp2[0]]
finded_certain_data_in_file = [temp2[1]]
# print('TIME -', time.perf_counter() - time2)

data = [finded_certain_data_in_file]
# print(data)
# print('-'*100)
# print(data)

temp = is_requared_data(json_request, data)
n=1
while temp[0]:
    # print(temp)
    # print('-'*40)
    # print('REQUEST -', n, temp[1])
    finded_data = search(temp[1], 1) # РЕШЕНО. вот тут пробелма, что ллм в temp[1] выдает описание, а не строгий поиск
    # так же надо сделать поиск именно по значениям, а не по описанию файла finded_data
    code = finded_data[0][0]
    temp3 = get_data_with_code(user_request, code)
    codes_data.append(temp3[0])
    finded_certain_data_in_file = temp3[1]

    data.append(finded_certain_data_in_file)
    temp = is_requared_data(user_request, data)
    n+=1
    # print(data[0][0][0])

    if n==3: # сколько раз искать в базе данных - каждый запрос к яндексу идет около 30-60 секунд. Надо уточнить по скорости что делать
        # print(data)
        print(f'Произошло {n} попыток достать данные и не получилось')
        break

res_answer_llm = get_final_llm_answer(user_request, data)
res_answer_llm = re.sub(r"\*", "", res_answer_llm)



# print('\nTIME -', time.perf_counter()-start_time, '\n')
print(f'\n\nИСКАЛИ ДАННЫЕ В БАЗЕ: {n} раз\n\n')

for i in codes_data:
    print('Источник:', PARQUET_DIR / f"{i}.parquet")

# print(f'ИСПОЛЬЗОВАЛИ ДАННЫЕ: {[f'code: {i[0]}, name: {i[1]}' for i in data]}')
print(f'\n\nОТВЕТ: {res_answer_llm}\n\n')