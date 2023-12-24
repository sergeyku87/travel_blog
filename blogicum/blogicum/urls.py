from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

import debug_toolbar
'''
Привет, я делал отдельный список, но тесты ругаются,
я привел пример, как делал, в закомменетированной части кода
и ошибку из тестов
'''
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    #path('auth/', include('users.urls')),
    path('auth/registration/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += [path(
        '__debug__/',
        include(debug_toolbar.urls)
    )]

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

# client = <django.test.client.Client object at 0x0000026D18988190>

#     @pytest.mark.django_db
#     def test_custom_err_handlers(client):
#         try:
#             from blogicum import urls as blogicum_urls
#         except Exception:
#             raise AssertionError(
#                 "Убедитесь, в головном файле с маршрутами нет ошибок."
#             )
#         urls_src_squashed = squash_code(inspect.getsource(blogicum_urls))
#         if "django.contrib.auth.urls" not in urls_src_squashed:
# >           raise AssertionError(
#                 "Убедитесь, что подключены маршруты для работы с
#                    пользователями из"
#                 " `django.contrib.auth.urls`."
#             )
# E           AssertionError: Убедитесь, что подключены маршруты для работы
#            с пользователями из `django.contrib.auth.urls`.

# tests\test_users.py:35: AssertionError
