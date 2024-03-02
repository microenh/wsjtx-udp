import settings
if settings.platform == 'win32':
    from darkdetect import isDark
else:
    import subprocess

    def isDark():
        out = subprocess.run(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
            capture_output=True)
        stdout = out.stdout.decode()
        return 'noir' in stdout
