from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message
from .serializers import MessageSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        messages = self.get_queryset()
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class WebhookReceiverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        result_data = request.data.get('result', None)

        if result_data is not None:
            message_id = result_data.get('message_id', None)
            if message_id is not None:
                try:
                    message = Message.objects.get(pk=message_id)
                    message.result = result_data.get('result_value', None)
                    message.save()

                    return Response({'message': 'Result updated successfully'}, status=status.HTTP_200_OK)
                except Message.DoesNotExist:
                    return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Message id not provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Result data not provided'}, status=status.HTTP_400_BAD_REQUEST)


