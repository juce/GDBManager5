# setup.py
from distutils.core import setup
import py2exe


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "5.4.0"
        self.company_name = "Kitserver Ltd."
        self.copyright = "Copyright 2011 Juce"
        self.name = "GDB Manager 5"


################################################################
# A program using wxPython

# The manifest will be inserted as resource into test_wx.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# test_wx.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

gdbManager = Target(
    # used for the versioninfo resource
    description = "GDB Manager utility for Kitserver 5 GDB",

    # what to build
    script = "GDBManager.py",
    other_resources = [(RT_MANIFEST, 1, 
            manifest_template % dict(prog="GDBManager"))],
    #icon_resources = [(1, "icon.ico")],
    ##dest_base = "gdbManager"
)

setup(
    windows = [gdbManager],
        data_files=[
            (".",[
                "default.png","shorts-mask.png","shorts63-mask.png",
                "wizard.png","converter.txt", "msvcp71.dll"]),
            ("docs",[
                "docs/README.txt"])
        ]
)
