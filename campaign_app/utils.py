


def get_page_range(start, end, current):
    
    previous = current - 1 if current > start else None
    next_num = current + 1 if current < end else None
    page_range = [previous, current, next_num]
    page_range = page_range if start in page_range else ['First',*page_range]
    page_range = page_range if end in page_range else [*page_range, 'Last']
    return page_range