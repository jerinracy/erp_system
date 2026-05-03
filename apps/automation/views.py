from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Rule
from .serializers import RuleSerializer


class RuleCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RuleSerializer(data=request.data)

        if serializer.is_valid():
            rule = serializer.save(tenant=request.user.tenant)
            return Response(RuleSerializer(rule).data, status=201)

        return Response(serializer.errors, status=400)


class RuleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rules = Rule.objects.filter(tenant=request.user.tenant)
        serializer = RuleSerializer(rules, many=True)
        return Response(serializer.data)


class RuleUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            rule = Rule.objects.get(id=pk, tenant=request.user.tenant)
        except Rule.DoesNotExist:
            return Response({"error": "Rule not found"}, status=404)

        serializer = RuleSerializer(rule, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class RuleDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            rule = Rule.objects.get(id=pk, tenant=request.user.tenant)
        except Rule.DoesNotExist:
            return Response({"error": "Rule not found"}, status=404)

        rule.delete()
        return Response({"message": "Rule deleted"}, status=204)
