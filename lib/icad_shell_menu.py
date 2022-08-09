from lib.util import Colors
import lib.config_editor_handler as config_edit
import sys
version = "1.0"


def main_menu():
    choice = '0'
    while choice == '0':
        print(
            Colors.FG.Green + "+-----=> " + Colors.FG.LightBlue + "iCAD Shell:" + Colors.FG.Green + " <=-----+" + Colors.Reset)
        print(Colors.FG.Green + "=>" + Colors.FG.Yellow + " 1. " + Colors.FG.LightBlue + "Convert TTD tones.cfg" + Colors.Reset)
        print(Colors.FG.Green + "=>" + Colors.FG.Yellow + " 2. " + Colors.FG.LightBlue + "Add Post/Pre Recording to fd-tone-notify" + Colors.Reset)
        print(Colors.FG.Green + "=>" + Colors.FG.Yellow + " 3. " + Colors.FG.LightBlue + "Generate MQTT Client Topics" + Colors.Reset)
        print(Colors.FG.Green + "=>" + Colors.FG.Yellow + " 4. " + Colors.FG.LightBlue + "Exit" + Colors.Reset)
        print(
            Colors.FG.Green + "+---------=> " + Colors.FG.Yellow + "Version " + version + " " + Colors.FG.Green + "<=---------+" + Colors.Reset)

        choice = input(Colors.FG.Yellow + "Choose Menu Item: " + Colors.Reset)

        if choice == "4":
            sys.exit()
        elif choice == "3":
            config_edit.generate_mqtt_config()
        elif choice == "2":
            config_edit.add_external_command()
        elif choice == "1":
            config_edit.convert_ttd()
        else:
            print(Colors.FG.Red + Colors.Bold + "Invalid menu choice." + Colors.Reset)
            main_menu()