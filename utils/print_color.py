def print_color(message, code, return_color=False):
    """Prints or returns pretty colors -_o
    Param message (str): the message to print
    Param code (str): e = red, i = blue, g = green, w = yellow
    Param return_color (bool): returns the message and color code
    rather than printing it directly.
    """
    # Errors red
    if code == "e":
        if return_color:
            return "\033[91m[!] " + message + "\033[0m"
        print("\033[91m[!] " + message + "\033[0m")

    # Information blue
    if code == "i":
        if return_color:
            return "\033[95m[*] " + message + "\033[0m"
        print("\033[95m[*] " + message + "\033[0m")

    # Good green
    if code == "g":
        if return_color:
            return "\033[92m[+] " + message + "\033[0m"
        print("\033[92m[+] " + message + "\033[0m")

    # Warning yellow
    if code == "w":
        if return_color:
            return "\033[93m[*] " + message + "\033[0m"
        print("\033[93m[*] " + message + "\033[0m")