import argparse

cmdArgs = {}

def getArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("--theme", type=str, help="Theme of the app")
    parser.add_argument("--dpx", type=str, help="Enter dp id")

    args = parser.parse_args()
    cmdArgs["args"] = args
    print(f"{cmdArgs = }")
    return args

def getCmdArgs():
    return cmdArgs["args"]

def isDarkTheme():
    args = getCmdArgs()
    if args.theme == "dark":
        return True
    return False

def getDpId(args):
    return args.dpx