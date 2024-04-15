from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "ReceiptHub"
urlpatterns = [
    # path("", views.IndexView.as_view(), name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("create_account/", views.create_account, name="create_account"),
    path("upload/", views.upload_file, name="upload"),
    path("delete/<slug:file_uuid>", views.delete_receipt, name="delete"),
    path("receipts/", views.receipt_index_view, name="receipt_index"),
    path("receipts/<slug:file_uuid>/", views.receipt_view, name="receipt"),
    # path("receipts/", views.ReceiptIndexView.as_view(), name="receipt_index"),
    # path("receipts/<slug:file_uuid>/", views.ReceiptView.as_view(), name="receipt"),
    # path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)