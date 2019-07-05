def to_int(i, default=None):
    try:
        return int(i)
    except ValueError:
        return default

def get_pages_list(number_of_pages, current_page):    #Функция отдающая список для правильного формирования пагинации
    
    lst        = [i for i in range(1, number_of_pages + 1)]
    first_page = lst[0]
    last_page  = lst[len(lst) - 1]
    result     = []
    
    if number_of_pages <= 11:

        return range(1, number_of_pages + 1)

    if number_of_pages > 11 and current_page < 6:
        result.extend(lst[:9])
        result.append('...')
        result.append(last_page)
        
        return result
    
    if number_of_pages > 11 and current_page >= 6 and current_page not in lst[last_page - 4:last_page + 1]:
        result.append(first_page)
        result.append('...')
        result.extend(lst[current_page - 4:current_page + 3])
        result.append('...')
        result.append(last_page)
        
        return result
    
    if number_of_pages > 11 and current_page >= 6 and current_page in lst[last_page - 4:last_page + 1]:
        result.append(first_page)
        result.append('...')
        result.extend(lst[last_page - 9:last_page + 1])
        
        return result

        
