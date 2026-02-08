from django.urls import path
from . import views

app_name="admin-portal"

urlpatterns = [
    path('', views.index, name='index'),
    path('all-theatre', views.all_theatre, name='all-theatre'),
    path('theatre-detail/<int:pk>', views.theatre_detail, name='theatre-detail'),
    path('new-payout-payments/<int:pk>', views.new_payout_payments, name='new-payout-payments'),
    path('all-payouts', views.all_payouts, name='all-payouts'),
    path('payout-payments/<pk>', views.payout_payments, name='payout-payments'),
    path('update-payout-settlement/<pk>', views.update_payout_settlement, name='update-payout-settlement'),
    path('settings', views.settings, name='settings'),
    path('gateways', views.gateways, name='gateways'),
    path('activate-gateway/<pk>', views.activate_gateway, name='activate-gateway'),
    path('all-orders', views.all_orders, name='all-orders'),
    path('order-profile/<pk>', views.order_profile, name='order-profile'),
    # path('edit-theatre-detail/<pk>', views.edit_theatre_detail, name='edit-theatre-detail'),
    path('upload-food-image', views.upload_food_image, name='upload-food-image'),
    path('delete-order/<pk>', views.delete_order, name='delete-order'),
    path('download-report/<pk>', views.download_report, name='download-report'),
    path('item-approved-list', views.item_approved_list, name='item-approved-list'),
    path('upload-document/<int:pk>', views.upload_document, name='upload-document'),
    path('delete-document/<int:pk>', views.delete_document, name='delete-document'),
    path('user-aggriment/<int:pk>', views.user_aggriment, name='user-aggriment'),
    path('update-logo/<pk>', views.update_logo, name='update-logo'),
    path('update-gst-details/<pk>', views.update_gst_detail, name='update-gst-details'),
    path('update-bank-details/<pk>', views.update_bank_detail, name='update-bank-details'),
    path('approve-food-item/<int:pk>', views.approve_food_item, name='approve-food-item'),
    path('download-bulk-report', views.download_bulk_report, name="download-bulk-report"),
    path('create-single-payout', views.create_single_payout, name='create-single-payout'),
    path('all-queries', views.all_queries, name='all-queries'),
    path('update-query/<int:pk>', views.update_query, name='update-query'),
    path('compare-settlement-payout', views.compare_settlment_and_payout, name='compare-settlement-payout'),
    path('live-orders', views.live_orders, name='live-orders'),
    path('new-all-order', views.all_orders_new_page, name='new-all-order'),
    path('theatre-profile', views.theatre_profile, name="theatre-profile"),
    path('all-refund-queries', views.all_refund_queries, name='all-refund-queries'),
    path('download-hall-qr/<int:pk>', views.download_hall_qr, name='download-hall-qr'),
    path('refund-order/<int:pk>', views.refund_order, name='refund-order'),
    path('get-db-files', views.get_db_files, name='get-db-files'),

]