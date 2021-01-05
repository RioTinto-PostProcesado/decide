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
         * type: IDENTITY | ORDER
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        t = request.data.get('type')
        opts = request.data.get('options', [])

        if t == 'IDENTITY':
            return self.identity(opts)
        
        elif t == 'ORDER':
            return Response(self.order(opts))

        return Response({})
