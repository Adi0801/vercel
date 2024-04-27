from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.contrib.auth.models import User #default user table in model
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.auth import authenticate,login,logout

# email = EmailMessage(
#     "Hello",
#     "Body goes here",
#     "from@example.com",
#     ["to1@example.com", "to2@example.com"],
#     ["bcc@example.com"],
#     reply_to=["another@example.com"],
#     headers={"Message-ID": "foo"},
# )

# Create your views here.
@csrf_exempt
def handlesignup(request):
    # print("I am Running")
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST["pass1"]
        Confirm_password=request.POST["pass2"]
        if password!=Confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,"signup.html")

            # return HttpResponse("Password incorrect")
            # return render(request,'auth.signup.html')
        try:
            if User.Object.get(username=email): #printing email in frontend
                 messages.info(request,"Email is Taken")
                # return HttpResponse("Email Already Exist")
                 return render(request,'signup.html')
        except Exception as e:
            pass

        user=User.objects.create_user(email,email,password) #In user table -username,email,pass
        user.is_active=False #after email authecation user can login
        user.save()

        email_subject="Acivate Your Account"
        message=render_to_string('activateuser.html',{
            'user':user,
            'domain':'127.0.0.1:8000', #after deploumnet give that domain name
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),  #for particular user we generate binary key in particular format
            'token':generate_token.make_token(user)
        })

       

        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,
            ["email"])
        email_message.send()
        message.success(request,"Activate Your Acccount by clicking link in your gmail")
        return redirect('/auth/login/')
    return render(request,"signup.html")

        # return HttpResponse("User created", email)
    # return render(request,"signup.html")


class ActivateUserAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as e:
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/auth/login')
        return render(request,'activatationfailed.html')



def handlelogin(request):
    if request.method=='POST':
        username=request.POST['email']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)
        
        if myuser is not None:
            login(request,myuser)#whatever request give acess to myuser
            messages.success(request,"Login Success")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/auth/login')
    return render(request,"login.html")
    


def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    # return to the login function
    return redirect('/auth/login') 
 