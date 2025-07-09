import time
from django.http import HttpResponseForbidden

forbiddenip=["192.168.29.222","192.168.29.226"]

class PrintRequestPathMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self,request):
        print(f"user visited URL: {request.path}")

        response = self.get_response(request)

        return response
    


class TimerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        print(f"{request.path} {duration:.2f}s")
        return response



# class RestrictIpMiddleware():
#     def __init__(self,get_response):
#         self.get_response=get_response


#     def get_client_ip(self,request):
#         x_forwarded_for=request.META.get("HTTP_X_FORWARDED_FOR")
#         # Determine the client's IP address:
#         # - If the request passed through a proxy, the 'X-Forwarded-For' header may contain a list of IPs.
#         #   The first IP in this list is typically the original client's IP.
#         # - If not present, fall back to 'REMOTE_ADDR', which is the direct client's IP.
#         # This logic helps accurately identify the real client, even when proxies are involved.
    
#         '''
#         terms used:
#         - x_forwarded_for: A header that may contain the original IP address of a client when the request passes through a proxy.
#         - REMOTE_ADDR: A server variable that contains the IP address of the client making the request.
#         - request.META: A dictionary-like object containing all available HTTP headers and server variables.
#         - request: The HTTP request object that contains metadata about the request, including headers.
#         - get_client_ip: A method to extract the client's IP address from the request.  
#         - proxy: An intermediary server that forwards requests from clients to other servers.
#         - original client's IP: The actual IP address of the user making the request, which may be obscured by proxies.
#         '''
        
#         if x_forwarded_for:
#             ip = x_forwarded_for.split(',')[0].strip()
#         else:
#             ip = request.META.get("REMOTE_ADDR")
        
#         return ip


#     def __call__(self,request):
#         ip=self.get_client_ip(request)
#         if ip in forbiddenip:
#             return HttpResponseForbidden("you are not a authorized user")
        
#         return self.get_response(request)
