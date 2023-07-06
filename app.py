from manager import ConsultaSheet
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-opt', '--option', type=int,
                    help="Chose a option: 1 - Figure out the better combination | 2 - Search distances")
parser.add_argument('-oc', '--origincolumn', default='Origem', type=str,
                    help='Specify the name of the column with the origins | Default: "Origem"')
parser.add_argument('-dc', '--destinycolumn', default='Destino', type=str,
                    help='Specify the name of the column with the destinys | Default: "Destino"')
parser.add_argument('-of', '--originfile', type=str, help='Specify the name of the file with the origins.')
parser.add_argument('-df', '--destinyfile', type=str, help='Specify the name of the file with the destinys')
parser.add_argument('-f', '--file', default=None, type=str, help="In one file with both information cases.")
parser.add_argument('-bs', '--batchsize', default=10, type=int)

args = parser.parse_args()

if args.file is not None:
    consulta = ConsultaSheet(option=args.option,
                             sheet1=args.file,
                             sheet2=args.file,
                             colunaorigem=args.origincolumn,
                             colunadestino=args.destinycolumn,
                             batchsize=args.batchsize
                             )
else:
    consulta = ConsultaSheet(option=args.option,
                             sheet1=args.originfile,
                             sheet2=args.destinyfile,
                             colunaorigem=args.origincolumn,
                             colunadestino=args.destinycolumn,
                             batchsize=args.batchsize)

consulta.compare()
