from rest_framework.response import Response

def customeFailResponse(message):
    print('message is: ', message)
    return Response({
        "status": False,
        "message": message
    })