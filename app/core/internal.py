import random
import string


def generate_random_string(len):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(len))


def paginate_info(total_items, current_page, items_per_page):
    total_pages = (total_items + items_per_page - 1) // items_per_page
    is_first_page = current_page == 1
    is_last_page = current_page == total_pages
    has_previous_page = current_page > 1
    has_next_page = current_page < total_pages

    offsets = [-2, -1, 1, 2]
    candidate_pages = [current_page + offset for offset in offsets]
    valid_pages = [page for page in candidate_pages if 1 <= page <= total_pages]
    valid_pages.append(current_page)
    # valid_pages.sort()
    # if len(valid_pages) < 4:
    valid_pages.append(1)
    valid_pages.append(total_pages)
    v_pages = [i for i in set(valid_pages)]
    v_pages.sort()

    print(v_pages)
    result = [v_pages[0]]
    for i in range(1, len(v_pages)):
        if v_pages[i] - v_pages[i - 1] > 1:
            result.append(-1)
            result.append(v_pages[i])
        else:
            result.append(v_pages[i])
    print({
        'current_page': current_page,
        'items_per_page': items_per_page,
        'total_pages': total_pages,
        'total_items': total_items,
        'is_first_page': is_first_page,
        'is_last_page': is_last_page,
        'has_previous_page': has_previous_page,
        'has_next_page': has_next_page,
        'adjacent_pages': result
    })
    return {
        'current_page': current_page,
        'items_per_page': items_per_page,
        'total_pages': total_pages,
        'total_items': total_items,
        'is_first_page': is_first_page,
        'is_last_page': is_last_page,
        'has_previous_page': has_previous_page,
        'has_next_page': has_next_page,
        'adjacent_pages': result
    }