# from django.shortcuts import redirect
# from django.urls import reverse
# from django.conf import settings

# class LoginRequiredMiddleware:
#     def __init__(self,get_response):
#         self.get_response = get_response
    
#     def __call__(self,request):
#         #URLs that don't require authentication
#         exempt_urls = [
#             reverse('account_login'),
#             reverse('account_logout'),
#             reverse('account_signup'),
#             '/accounts/',
#             '/admin/',
#         ]

#         # check if user is autheticated
#         if not request.user.is_authenticated:
#             #check if current path requires authentication
#             if not any(request.path.startswith(url) for url in exempt_urls):
#                 return redirect('account_login')
        
#         response=self.get_response(request)
#         return response