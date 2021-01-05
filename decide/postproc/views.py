from rest_framework.views import APIView
from rest_framework.response import Response
import math


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            });

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)
    
    def order(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': 0,
            });

        out.sort(key=lambda x: -x['votes'])

        votesTotal=0

        for votes in out:
            votesTotal=votesTotal+votes['votes']

        max=len(options)*votesTotal

        a=0

        while a < len(out):
            postproc_a=max-out[a]['votes']
            out[a]['postproc']=postproc_a
            a=a+1

        return out

    def post(self, request):
        """
         * type: IDENTITY | PARIDAD | ORDER
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        typeOfData = request.data.get('type', 'IDENTITY')
        options = request.data.get('options', [])

        if typeOfData == 'IDENTITY':
            return self.identity(options)

        elif typeOfData == 'PARIDAD':
            check = self.check_json(options)
            if check:
                return Response(self.paridad(options))
            else:
                return Response({'message' : 'No se cumplen los ratios de paridad 60%-40%'})
        
        elif typeOfData == 'ORDER':
            return Response(self.order(opts))

        return Response({})
