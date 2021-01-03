from rest_framework.views import APIView
from rest_framework.response import Response


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

    def sin_paridad(self, options):

        out = []

        for opt in options:

            out.append({
                **opt,
                'paridad': [],
            })

        for i in out:

            escanyos = i['postproc']
            presentados = i['presentados']
            x = 0

            while escanyos > 0:
              

                i['paridad'].append(presentados[x])
                x = x + 1

                escanyos = escanyos - 1 

        return out
            
    def post(self, request):
        """
         * type: IDENTITY | EQUALITY | WEIGHT
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        t = request.data.get('type', 'IDENTITY')
        opts = request.data.get('options', [])

        if t == 'IDENTITY':
            return self.identity(opts)

        return Response({})
