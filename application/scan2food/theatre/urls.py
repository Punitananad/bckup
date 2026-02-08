from django.urls import path, include
from . import views

app_name="theatre"
urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(('theatre.api_urls', 'theatre-api'), namespace='theatre-api')),
    path('all-seats', views.live_orders, name='all-seats'),
    path('seat-view', views.seat_view, name='seat-view'),
    path('live-orders', views.live_orders, name='live-orders'),
    path('add-hall', views.add_hall, name='add-hall'),
    path('add-seat-to-hall/<int:pk>', views.add_seat_to_hall, name='add-seat-to-hall'),
    path('setting', views.theatre_setting, name='setting'),
    path('add-menu', views.add_menu, name='add-menu'),
    path('add-category', views.add_category, name='add-category'),
    path('add-food-item', views.add_food_item, name='add-food-item'),
    path('upload-menu', views.upload_menu, name='upload-menu'),
    path('change-availablity/<pk>', views.change_availablity, name='change-availablity'),
    path('add-food-item/<int:pk>', views.add_food_item, name='edit-food-item'),
    path('delete-food-item', views.delete_food_item, name='delete-food-item'),
    path('delete-food-category/<int:pk>', views.delete_food_category, name='delete-food-category'),
    path('theatre-detail', views.theatre_detail, name='theatre-detail'),
    path('add-tax', views.add_tax, name='add-tax'),
    path('remove-tax/<int:pk>', views.remove_tax, name='remove-tax'),
    path('all-orders', views.all_orders, name='all-orders'),
    path('all-payments', views.all_payments, name='all-payments'),
    path('all-payouts', views.all_payouts, name='all-payouts'),
    path('payout-payments/<pk>', views.payout_payments, name='payout-payments'),
    path('cancel-cash-order/<int:pk>', views.cancel_cash_order, name='cancel-cash-order'),
    path('order-profile/<int:pk>', views.show_order_profile, name='order-profile'),
    path('print-bill/<int:pk>', views.print_bill, name='print-bill'),
    path('print-kot/<int:pk>', views.print_kot, name='print-kot'),
    path('order-status/<int:pk>', views.order_status, name='order-status'),
    path('order-feedback/<int:pk>', views.order_feedback, name='order-feedback'),
    path('generate-cash-order/<int:pk>', views.generate_cash_order, name='generate-cash-order'),
    path('waiting-for-cash-order/<int:pk>', views.waiting_for_cash_order, name='waiting-for-cash-order'), #Razorpay, Cashfree
    path('add-payment-manually/<int:pk>', views.add_cash_payment, name='add-payment-manually'),
    path('initiate-payment/<int:pk>', views.initiate_payment, name='initiate-payment'),
    path('get-seat-last-order/<int:pk>',views.get_seat_last_order, name='get-seat-last-order'),
    path('show-menu/<int:pk>', views.show_menu, name='show-menu'),
    path('single-qr/<int:pk>', views.single_qr, name='single-qr'),
    path('hall-qr/<int:pk>', views.hall_qr, name='hall-qr'),
    path('all-users', views.all_users, name='all-users'),
    path('create-simple-user', views.create_simple_user, name='create-simple-user'),
    path('seat-qr', views.seat_qr, name='seat-qr'),
    path('new-seat-qr', views.new_seat_qr, name='new-seat-qr'),
    path('new-qr', views.new_qr, name='new-qr'),
    path('acrylic-small-qr', views.acrylic_small_qr, name='acrylic-small-qr'),
    path('refund-order/<int:pk>', views.refund_order, name='refund-order'),
    path('partial-refund-order/<int:pk>', views.partial_refund_order, name='refund-order'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('update-scaning-service', views.update_scaning_service, name='update-scaning-service'),
    path('otp-details', views.otp_details, name='otp-details'),
    path('raise-refund-request/<int:pk>', views.raise_refund_request, name='raise-refund-request'),
    
    # INVOICE
    path('invoice/<int:pk>', views.invoice, name='invoice'),
    
    # INITATE PAYMENT
    path('initiate-test-payment/<int:pk>', views.initiate_test_payment, name='initiate-test-payment'),
    
    # CCAVENUE PAYMENT REQUEST HANDER
    path('ccavenue-payment-request-handler/<int:pk>', views.ccavenueRequestHandler, name='ccavenue-payment-request-handler'),

    # PAYMENT CALLBACKS
    # RAZORPAY PAYMENT CALLBACAK
    path('razorpay-payment-callback', views.razorpay_payment_callback, name='razorpay-payment-callback'),
    # SPLIT RAZORPAY PAYMENT CALLBACK
    path('split-razorpay-payment-callback', views.split_razorpay_payment_callback, name='split-razorpay-payment-callback'),
    #  CASFREE PAYMENT CALLBACK
    path('cashfree-payment-callback/<int:pk>', views.cashfree_payment_callback, name='cashfree-payment-callback'),
    # PHONEPE PAYMENT CALLBACK
    path('phonepe-payment-callback/<int:pk>', views.phonepe_payment_callback, name='phonepe-payment-callback'),
    # PAYU PAYMENT CALLBACK
    path('payu-payment-callback/<int:pk>', views.payu_payment_callback, name='payu-payment-callback'),
    # CCAvenue PAYMENT CALLBACK
    path('ccavenue-payment-callback/<int:pk>', views.ccavenue_payment_callback, name='ccavenue-payment-callback'),

    # ALL REVIEWS
    path('all-reviews', views.all_reviews, name='all-reviews'),
    # ALL REFUND QUERIES
    path('all-refund-queries', views.all_refund_queries, name='all-refund-queries'),
]