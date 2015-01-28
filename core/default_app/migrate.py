#!/usr/bin/env python
from distutils.util import strtobool
from mapex.src.Adapters import NoTableFound
from z9.core.models import Contours
from z9.core.utils import bcolors
from optparse import OptionParser

try:
    from application import application
except NoTableFound:
    pass

if __name__ == "__main__":
    cli = OptionParser()
    cli.add_option(
        "-q",
        "--quiet",
        action="store_false",
        default=True,
        dest="verbose",
        help="don't print to stdout"
    )
    cli.add_option(
        "-c",
        "--contour",
        choices=list(Contours.__members__),
        default="UNITTESTS"
    )

    options, args = cli.parse_args()

    # Миграции баз данных приложения
    application.contour = Contours[options.contour]

    if not len(application._databases):
        if options.verbose:
            print("{color}There are no databases{end}".format(color=bcolors.WARNING, end=bcolors.ENDC))
        exit()

    # noinspection PyProtectedMember
    for db in application._databases:
        if options.verbose:
            print("Contour: %s" % options.contour)
            print("DSN: %s" % str(db.pool._dsn))

            confirmation = input('{color}continue migration?{end} {color2}(y or N){end}'.format(color=bcolors.FAIL, color2=bcolors.OKGREEN, end=bcolors.ENDC))
            if strtobool(confirmation if len(confirmation) else 'N'):
                db.migrate(verbose=options.verbose)
            else:
                print("{color}  .. migration canceled{end}".format(color=bcolors.FAIL, end=bcolors.ENDC))
            print("\n")
        else:
            db.migrate(verbose=options.verbose)
