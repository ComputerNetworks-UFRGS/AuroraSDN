from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Receives a list of objects, a request object, and a number of pages
def paginate(obj_list, request, obj_per_page = 10):

    paginator = Paginator(obj_list, obj_per_page)  # Show 10 objects per page
    p = request.GET.get('p')
    try:
        obj_list = paginator.page(p)
    except (PageNotAnInteger, TypeError):
        # If page is not an integer, deliver first page.
        obj_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        obj_list = paginator.page(paginator.num_pages)

    return obj_list
