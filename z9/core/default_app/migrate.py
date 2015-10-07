#!/usr/bin/env python
from distutils.util import strtobool
from mapex.Adapters import NoTableFound
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
        "-f",
        "--force",
        action="store_true",
        default=False,
        dest="force",
        help="apply migrations without confirmation"
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
        print("{color}There are no databases{end}".format(color=bcolors.WARNING, end=bcolors.ENDC))
        exit()

    # noinspection PyProtectedMember
    for db in application._databases:
        print("Contour: %s" % options.contour)
        print("DSN: %s" % str(db.pool._dsn))

        if options.force:
            confirmation = 'Y'
        else:
            confirmation = input('{color}continue migration?{end} {color2}(Y or n){end}'.format(
                color=bcolors.WARNING,
                color2=bcolors.OKGREEN,
                end=bcolors.ENDC)
            ) or 'Y'

        if strtobool(confirmation):
            db.migrate()
        else:
            print("{color}  .. migration canceled{end}".format(color=bcolors.FAIL, end=bcolors.ENDC))
        print("\n")
