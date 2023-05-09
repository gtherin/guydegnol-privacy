import argparse
import datetime
import os
import sys
import time
import json


def get_opts(opt_key, opts):
    if opt_key not in opts:
        return opts

    lindex_start = opts.index(opt_key) + 1
    lindex_end = len(opts)
    for i, o in enumerate(opts[lindex_start + 1 :]):
        if len(o) == 2 and o[0] == "-":
            lindex_end = lindex_start + i + 1
            break

    label = " ".join(opts[lindex_start:lindex_end])
    return opts[:lindex_start] + [label] + opts[lindex_end:]


def get_argparser(line, cell):
    parser = argparse.ArgumentParser(description="Evaluation params")
    parser.add_argument("-u", "--user", default=os.environ["STUDENT"] if "STUDENT" in os.environ else None)
    parser.add_argument("-i", "--id", default=None)
    parser.add_argument("-o", "--options", default="")
    parser.add_argument("-l", "--label", type=str, default="")
    parser.add_argument("-t", "--type", default="code")
    parser.add_argument("-x", "--xoptions", default=None)
    parser.add_argument("-w", "--widgets", default=None)
    parser.add_argument("-p", "--puppet", default="")
    parser.add_argument("-d", "--default", default="")

    try:
        opts = line.split()
        opts = get_opts("-l", opts)
        opts = get_opts("-d", opts)
        opts = get_opts("-o", opts)

        args = parser.parse_args(opts)

    except SystemExit as e:
        parser.print_help()
        return None

    if args.widgets is None:
        if args.type == "code_project":
            args.widgets = "w|tsc"
        elif args.type in ["table", "checkboxes"]:
            args.widgets = "lw|sc"
        elif args.type in ["code", "markdown", "formula"]:
            args.widgets = "sc"
        else:
            args.widgets = "lwsc"

    return args

    # from .widgets import check_widget
    # return check_widget(args)


def get_install_parser(argv):
    parser = argparse.ArgumentParser(
        description="Installation script evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-u", "--user", default=None)
    parser.add_argument("-x", "--pass-code", help="Pass code", default=None)
    parser.add_argument("-X", "--pass-phrase", help="Pass code", default=None)
    parser.add_argument("-e", "--env-id", help=f"Environnment id")
    parser.add_argument("-i", "--id", default=None)
    parser.add_argument("-p", "--packages", default="")
    parser.add_argument("-f", "--in-french", help="Change languages", action="store_true")
    parser.add_argument("-k", "--api-key", default="YOUR_KEY")
    parser.add_argument("-t", "--token", default="", help="YOUR_BK_KEY")
    parser.add_argument("-a", "--atoken", default="", help="YOUR_BKA_KEY")

    api_key = argv[argv.index("-k") + 1] if "-k" in argv else "YOUR_KEY"

    if "-k" in argv:
        argv[argv.index("-k") + 1] = "YOUR_KEY"

    argv = parser.parse_args(argv)
    argv.api_key = api_key

    return argv


def main(argv=sys.argv[1:]):
    args = get_install_parser(argv)

    # Set up a colab flag
    is_colab = os.path.exists("/content")

    if args.pass_phrase != "POLPETTE":
        print("RUN install bulkhours: aborted 💥, package is no more available")
        return

    # Log datetime
    start_time = time.time()
    stime = datetime.datetime.now() + datetime.timedelta(seconds=3600) if is_colab else datetime.datetime.now()
    print("RUN install bulkhours [%s]" % stime.strftime("%H:%M:%S"))

    # Set up the package directory
    bulk_dir = "/content" if is_colab else "/home/guydegnol/projects"
    env_id = "colab" if is_colab else "mock"

    # Install main package
    if is_colab:
        if args.atoken != "":
            print(
                "RUN git clone https://github.com/guydegnol/bulkhours_admin.git [%s, %.0fs]"
                % (env_id, time.time() - start_time)
            )
            os.system(
                f"cd {bulk_dir} && rm -rf bulkhours_admin 2> /dev/null && git clone https://{args.atoken}@github.com/guydegnol/bulkhours_admin.git --depth 1 > /dev/null 2>&1"
            )
        print(
            "RUN git clone https://github.com/guydegnol/bulkhours.git [%s, %.0fs]" % (env_id, time.time() - start_time)
        )
        os.system(
            f"cd {bulk_dir} && rm -rf bulkhours 2> /dev/null && git clone https://github.com/{args.token}@guydegnol/bulkhours.git --depth 1 > /dev/null 2>&1"
        )

    if args.packages != "":
        # Update pip
        print("RUN pip install --upgrade pip [%s, %.0fs]" % (env_id, time.time() - start_time))
        if is_colab:
            os.system(f"pip install --upgrade pip > /dev/null 2>&1")

        # Install packages
        for package in args.packages.split(","):
            if package not in ["wkhtmltopdf"]:
                print("RUN pip install %s [%s, %.0fs]" % (package, env_id, time.time() - start_time))
                os.system(f"pip install {package} > /dev/null 2>&1")
            else:
                print("RUN apt install %s [%s, %.0fs]" % (package, env_id, time.time() - start_time))
                os.system(f"apt install {package} > /dev/null 2>&1")

    # Dump env variables
    data = {
        "login": args.user,
        "pass_code": args.pass_code,
        "env": args.env_id,
        "nid": args.id,
        "in_french": args.in_french,
        "api_key": args.api_key,
    }
    print(
        "LOG login= %s, id=%s, env=%s [%s, %.0fs]"
        % (args.user, args.id, args.env_id, env_id, time.time() - start_time)
    )
    with open(f"{bulk_dir}/bulkhours/.safe", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
