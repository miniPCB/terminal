import sys
from PyQt5.QtWidgets import QApplication
from miniPCB.minipcb_terminal import MinipcbTerminal

def main():
    app = QApplication(sys.argv)
    terminal = MinipcbTerminal()
    terminal.check_for_updates()  # Check for updates before showing the window
    terminal.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
