#!/usr/bin/env python
# coding: utf-8

# In[115]:


import geopandas
import os
import zipfile
import matplotlib.pyplot as plt
import time


#### Декоратор ####


def timeit(verbose):
    def deco(func):

        def wrapper(*args):
            if verbose:
                start = time.time()
                func(*args)
                stop = time.time()
                with open('result/log_file.txt', 'a') as log_file:  # Запись лог-файла с временем работы функций
                    log_file.write(f"время начала работы функции '{func.__name__}' : {time.ctime(start)}\n"
                                   f"время окончания работы функции '{func.__name__}' : {time.ctime(stop)}\n"
                                   f"длительность выполнения функции '{func.__name__}' : {stop - start}\n\n")
            else:
                start = time.time()
                func(*args)
                stop = time.time()
                with open('result/log_file.txt', 'a') as log_file:  # Запись лог-файла с временем работы функций
                    log_file.write(f"длительность выполнения функции '{func.__name__}' : {stop - start}\n\n")

        return wrapper

    return deco


###### Функция первого задания ##############


@timeit(verbose=True)
def stat_data(gdf):
    # формирование сводной таблицы
    df = gdf.groupby('CATEGORY')['CATEGORY'].agg(['count', lambda x: f'{x.count() * 100 / len(gdf):.0f}'])
    df.columns = ['Количество', '% от общего числа']
    df['Категория'] = df.index
    # формируем круговую диаграмму со сводной таблицей и сохраняем в файл
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))
    ax2.axis('off')
    ax1.pie(df[df.columns[1]], labels=df.index, autopct='%1.0f%%')
    ax2.table(cellText=df.values, colLabels=df.columns, bbox=[0.25, 0.8, 0.6, 0.3])
    fig.savefig('result/pie_plot.pdf')


####################### Функции второго задания #############################

@timeit(verbose=False)
def new_poly(*args):
    new_id, geom, val, c = [], [], [], 0

    for x, y in intersect_poly(gdf):  # проход по списку кортежей с индексами пересекающихся полигонов
        gdf_new = gdf['geometry'][x].intersection(gdf['geometry'][y])  # формирует полигон пересечения
        s_new = gdf_new.area
        s_poly_1 = gdf['geometry'][x].area
        s_poly_2 = gdf['geometry'][y].area
        value_1 = gdf['VALUE'][x]
        value_2 = gdf['VALUE'][y]
        value = (s_new / s_poly_1) * value_1 + (s_new / s_poly_2) * value_2
        geom.append(gdf_new)  # список полигонов пересечения
        val.append(round(value, 1))  # список значений VALUE
        new_id.append(f'NEW_POLY_{c + 1}')  # список значений ID
        c += 1
    res_shp = geopandas.GeoDataFrame(
        {'ID': new_id, 'value': val, 'geometry': geom})  # формитрует GDF и выгружает в Shape-файл
    res_shp.to_file('result/new_test.shp')


# функция создания Списка кортежей из индексов пересекающихся полигонов
def intersect_poly(*args):
    a = 0
    list_poly_intersect = []
    for x in gdf['geometry']:
        b = 0
        for y in gdf['geometry']:
            if a != b and x.intersects(
                    y):  # исключает пересечения полигонов с самим собой и проверяет наличие пересечения
                if a > b:  # приводит к единому виду кортежи типа (a,b) || (b,a) == (a,b)
                    list_poly_intersect.append((b, a))
                else:
                    list_poly_intersect.append((a, b))
            b += 1
        a += 1
    return set(list_poly_intersect)  # исключает повторяющиеся кортежи


# задать рабочую директорию и сохранить в нее архив с Shape-файлом    
work_dir = 'C:/../work_dir'
os.chdir(work_dir)
zip_f = zipfile.ZipFile('test_polygons.zip')
zip_f.extractall()

# находим нужный файл после распаковки архива в рабочей директории и читаем его
for path, dir, file in os.walk(os.getcwd()):
    for x in file:
        if x == 'test.shp':
            gdf = geopandas.read_file(os.path.join(path, x))

# создаем директорию с результатами работы        
if not os.path.isdir('result'):
    os.mkdir('result')

stat_data(gdf)  # функция первого задания
new_poly(gdf)  # функция вотрого задания
