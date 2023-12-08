"""
Author：binxin
Date：2023/12/6 16:16
"""
import numpy as np
import pandas as pd
from iFinDPy import *
import datetime


# 登录函数
def login(username, password):
    thsLogin = THS_iFinDLogin(username, password)
    if thsLogin != 0:
        print('登录失败')
    else:
        print('登录成功')


# 获取数据
def get_data(edate):
    get_str = 'edate=' + edate + ';zqlx=全部'
    # jydm交易代码
    # f027转换价值
    # f022转股溢价率
    data_p00868 = THS_DR('p00868', get_str, 'jydm:Y,p00868_f027:Y,p00868_f022:Y', 'format:list')
    # print(data_p00868.data)
    if data_p00868.data is None:
        print(data_p00868.errmsg)
    return data_p00868


# 获取债券余额数据
def get_balance(jydm, date):
    data = THS_DS(jydm, 'ths_bond_balance_bond', '', '', date, date, 'format:list')
    if data.data is None:
        print(data.errmsg)

    return data.data[0]['table']['ths_bond_balance_bond']


# 保存数据到Excel
def save_to_excel(file_name, str_date, premium):
    if not os.path.exists(file_name):
        data = {"日期": [str_date], "转股溢价率%": [premium]}
        df = pd.DataFrame(data)
    else:
        df = pd.read_excel(file_name)
        new_data = pd.DataFrame({"日期": [str_date], "转股溢价率%": [premium]})
        df = pd.concat([df, new_data], ignore_index=True)

    df.to_excel(file_name, index=False)


# 计算中位数
def calculate_median(data, date):
    max_value = 100
    min_value = 80

    max_balance = 100
    min_balance = 5

    float_values = []

    data_jydm = data['jydm']
    data_f022 = data['p00868_f022']
    data_f027 = data['p00868_f027']

    for jydm, f027, f022 in zip(data_jydm, data_f027, data_f022):
        if '--' in f027 or '--' in f022:
            continue

        data_balance = get_balance(jydm, date)
        print(data_balance)
        f027_value = float(f027)
        f022_value = float(f022)

        if min_value < f027_value <= max_value and min_balance < data_balance[0]:
            float_values.append(f022_value)

    return np.median(float_values) if float_values else None


# 获取数据 - 区间
def get_interval_data(start_date, end_date):
    delta = datetime.timedelta(days=1)
    data_list = []

    while start_date <= end_date:
        print(start_date)
        edate = start_date.strftime("%Y%m%d")
        data = get_data(edate)
        if data.data is not None:
            data_list.append((start_date.strftime("%Y-%m-%d"), data))
        start_date += delta

    return data_list


# 主函数
def main():
    username = "账号"
    password = "密码"
    login(username, password)

    start_date = datetime.date(2023, 12, 8)
    end_date = datetime.date(2023, 12, 8)
    interval_data = get_interval_data(start_date, end_date)

    for date, data in interval_data:
        median_value = calculate_median(data.data[0]['table'], date)
        if median_value is not None:
            save_to_excel("转股溢价率记录.xlsx", date, median_value)


if __name__ == '__main__':
    main()
