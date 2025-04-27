from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user




# яку базу даних використовувати
#  і який сенс змінювати гілку якщо я сам виконую
# 2 рази виклик клін та сейв
# тести юзера

"""
 який сенс змінювати гілку якщо я сам виконую
чому запити action через постман а не браузер
що відображатись в полях юзера
"""