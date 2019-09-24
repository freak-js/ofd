from ofd.settings import BASE_DIR


def to_int(i, default=None):
    try:
        return int(i)
    except ValueError:
        return default

'''
get_pages_list - принимает два обязательных аргумента 
(количество страниц : int, запрашиваемая страница : int)
возвращает list() по которому происходит итерация в шаблоне.
'''
def get_pages_list(number_of_pages: int, current_page: int) -> list:
    lst = [i for i in range(1, number_of_pages + 1)]

    if number_of_pages <= 11:
        return lst

    first_page, last_page, result = lst[0], lst[-1], []

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


'''
sort_logs - не принимает аргументов, открывает файл logging.log 
сортирует логи по четырем спискам и возвращает список из этих списков.
'''
def sort_logs() -> list:
    info, warning, error, critical = [], [], [], []

    with open(BASE_DIR + '/logging.log') as log_file:
        for log in reversed(list(log_file)):    

            if 'INFO' in log:
                info.append(log)
            
            if 'WARNING' in log:
                warning.append(log)

            if 'ERROR' in log:
                error.append(log)

            if 'CRITICAL' in log:
                critical.append(log)
    return [info, warning, error, critical]