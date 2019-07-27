def to_int(i, default=None):
    try:
        return int(i)
    except ValueError:
        return default

#Функция отдающая список для правильного формирования пагинации
def get_pages_list(number_of_pages, current_page):
    lst = [i for i in range(1, number_of_pages + 1)]

    if number_of_pages <= 11:
        return lst
    
    if current_page > number_of_pages:
        current_page = number_of_pages

    first_page = lst[0]
    last_page  = lst[len(lst) - 1]
    result     = []

    if current_page < 7:
        result.extend(lst[:9])
        result.append('...')
        result.append(last_page)
    elif current_page not in lst[last_page - 6:last_page + 1]:
        result.append(first_page)
        result.append('...')
        result.extend(lst[current_page - 4:current_page + 3])
        result.append('...')
        result.append(last_page)
    else:
        result.append(first_page)
        result.append('...')
        result.extend(lst[last_page - 9:last_page + 1])
    return result
