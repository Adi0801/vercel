from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Products,OrderUpdate,Orders
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from Paytm import Checksum

# Create your views here.
def index(request):
    #divide the row based upon the category 
    allProducts=[]
    cat_products=Products.objects.values('category','id') #FILTERING CATEGORY BASED UPON TWO PARAMS
    cats={item['category'] for item in cat_products}
    for cat in cats:
        product=Products.objects.filter(category=cat)  #filter based on the category wise
        n=len(product) #NO OF PRODUCTS IN ONE CATEGORY
        nSlides=n//4+ceil((n/4)-(n//4)) #FOR DISLYING PRODUCTS IN A ROW
        allProducts.append([product,range(1,nSlides),nSlides])

    params={'allProducts':allProducts} #list pass as a dictionary  
    
    return render(request,"index.html",params)

def contact(request):
    if request.method=="POST":
        name=request.POST.get("name") #id
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pno=request.POST.get("pno")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pno) #object for the class
        myquery.save()
        messages.info(request,"We Will get back to you soon.....")
        return render(request,"contact.html")
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")



import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to 'live' for production
    "client_id": "",
    "client_secret": ""
})

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
       
        # Save order details to database
        order = Orders.objects.create(
            items_json=items_json,
            name=name,
            amount=amount,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        # get the data from frontend
        order.save()
        update = OrderUpdate(order_id=Orders.order_id,update_desc="the order has been placed")
        update.save()
        thank = True #if false order is failed

 

        # Generate PayPal payment request
        oid = str(Orders.order_id) + "ShoppifyIndia"
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://127.0.0.1:8000/handlerequest/",
                "cancel_url": "http://127.0.0.1:8000/payment/cancel/"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": "Payment for Order #" + oid
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.method == "REDIRECT":
                    return redirect(link.href)
        else:
            print(payment.error)
            # Handle payment creation failure
            return render(request, 'payment_failed.html')
        

    return render(request, 'checkout.html')



from django.http import HttpResponseBadRequest

@csrf_exempt
def handlerequest(request):
    # Initialize response_dict outside the try block
    response_dict = {}

    if request.method == 'POST':
        form = request.POST

        try:
            # Extract form data
            for i in form.keys():
                response_dict[i] = form[i]

            # Check if the payment response indicates success
            if response_dict.get('paymentId') and response_dict.get('PayerID'):
                # Extract payment ID and payer ID
                paypal_payment_id = response_dict['paymentId']
                paypal_payer_id = response_dict['PayerID']


                # Fetch payment details from PayPal using payment ID
                payment = paypalrestsdk.Payment.find(paypal_payment_id)

                if payment.execute({"payer_id": paypal_payer_id}):
                    # Payment was successful
                    print('Order successful')
                    paypal_order_id = payment.id
                    paypal_amount = payment.transactions[0].amount.total

                    # Extract order ID from PayPal order ID
                    rid = paypal_order_id.replace("ShopifyIndia", "")
                    print(paypal_order_id,paypal_amount)

                    # Update order status in your database
                    filter2 = Orders.objects.filter(order_id=rid)
                    for post1 in filter2:
                        post1.oid = paypal_order_id
                        post1.amountpaid = paypal_amount
                        post1.paymentstatus = "PAID"
                        post1.save()
                    print("Run next function")
                else:
                    # Payment failed
                    print('Order was not successful because ' + payment.error)
            else:
                # Payment response is incomplete
                print("Payment response is incomplete")

        except KeyError as e:
            # Handle missing key error
            print(f"KeyError: {e}")
            return HttpResponseBadRequest("Invalid request: Missing key(s)")

    return render(request, 'paymentstatus.html', {'response': response_dict})


