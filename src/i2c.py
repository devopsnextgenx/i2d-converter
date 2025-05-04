# Let first parse the command line arguments
from pkg.utils.cmdArgs import getArgs
args = getArgs()

# start application logic from here!!!

from pkg.ui.appWindow import AppWindow

if __name__ == "__main__":
    print(f"{args.theme = }")
    print(f"{args.dpx = }")
    app = AppWindow()
    app.mainloop()
    