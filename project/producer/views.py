import requests

from rest_framework import viewsets, status
from rest_framework.decorators import action
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

    @action(detail=False, methods=['post'])
    def create_and_send_to_consumer(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message_instance = serializer.save()

        data_to_send = {'text': message_instance.text, 'timestamp': message_instance.timestamp, 'id': message_instance.id}
        response = requests.post('http://localhost:8001/consumer/api/process-message/', json=data_to_send)

        # Process the response as needed
        result_from_consumer = response.json().get('result', None)

        return Response({'status': 'success'})


class WebhookReceiverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data_from_consumer = request.POST

        if data_from_consumer is not None:
            message_id = data_from_consumer.get('message_id')
            if message_id is not None:
                try:
                    message = Message.objects.get(pk=message_id)
                    message.result = data_from_consumer.get('result', None)
                    message.save()

                    return Response({'message': 'Result updated successfully'}, status=status.HTTP_200_OK)
                except Message.DoesNotExist:
                    return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Message id not provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Result data not provided'}, status=status.HTTP_400_BAD_REQUEST)


