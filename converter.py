import  wx
import  wx.wizard as wiz
import  os, os.path

#----------------------------------------------------------------------

def makePageTitle(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer

#---------------------------------------------------------------------------

"""
A dir choice with label
"""
class MyDirChoice(wx.Panel):
    def __init__(self, parent, labelText, dirs, key, dialogText="Select the folder"):
        wx.Panel.__init__(self, parent, -1)
        self.dirs = dirs
        self.key = key
        self.path = dirs[key]
        self.dialogText = dialogText
        self.label = wx.StaticText(self, -1, labelText, style=wx.ALIGN_RIGHT)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())
        self.dirButton = wx.Button(self, -1, "...", size=(30,1))

        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.hsizer.Add(self.dirButton, 0, wx.EXPAND | wx.RIGHT, border=10)
        
        self.text = wx.StaticText(self, -1, self.path, size=(300,80))
        self.text.SetFont(font)
        self.text.SetBackgroundColour(wx.Colour(230,230,230))

        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(self.hsizer, 0, wx.BOTTOM, border=10)
        self.vsizer.Add(self.text, 1)

        # bind events
        self.dirButton.Bind(wx.EVT_BUTTON, self.OnChooseDir)

        self.SetSizer(self.vsizer)
        self.Layout()

    def OnChooseDir(self, event):
        dlg = wx.DirDialog(self, self.dialogText, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.path = dlg.GetPath()
            if self.path[-1] != '\\': self.path += '\\'
            print "You selected %s" % self.path
            self.text.SetLabel(self.path)
            self.text.Wrap(300)
            # store path in a dictionary
            self.dirs[self.key] = self.path

#----------------------------------------------------------------------

class TitledPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)

class PageChooseKDB(wiz.WizardPageSimple):
    def __init__(self, parent, title, dirs):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)

        self.sizer.Add(wx.StaticText(self, -1, """
First, you need to select your KDB folder - the folder
named "KDB", where you current kits database is located.
"""))
        self.sizer.Add(MyDirChoice(self, "KDB", dirs, "KDB", "Select your KDB folder"))

class PageChooseGDB(wiz.WizardPageSimple):
    def __init__(self, parent, title, dirs):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)

        self.sizer.Add(wx.StaticText(self, -1, """
Now you need to choose a place where the new GDB will
be created. For example, if you want to make the new 
GDB right in your kitserver folder, then you should 
navigate to and select the "kitserver" folder.
"""))
        self.sizer.Add(MyDirChoice(self, "GDB location", dirs, "GDB", "Select a folder where GDB will be created"))

class MyStaticText(wx.StaticText):
    def __init__(self, parent, pattern, dictionary):
        wx.StaticText.__init__(self, parent, -1, pattern % dictionary)
        self.pattern = pattern
        self.dictionary = dictionary
        self.fulltext = self.GetLabel()
        self.SetSize((300,40))
        self.Wrap(300)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self,evt):
        text = self.pattern % self.dictionary
        if text != self.fulltext:
            self.SetLabel(self.pattern % self.dictionary)
            self.fulltext = self.GetLabel()
            self.Wrap(300)
        evt.Skip()


class PageConfirm(wiz.WizardPageSimple):
    def __init__(self, parent, title, dirs):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)

        self.sizer.Add(MyStaticText(self, """
Conversion is ready to begin.
Please, verify that your KDB and GDB folders are correct \
and then press "Next". If you want to change KDB or GDB location, \
you can go back and modify them on previous pages.

KDB: %(KDB)s
GDB: %(GDB)sGDB
""", dirs))

        self.dirs = dirs

        #self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)

    def OnWizPageChanged(self,evt):
        print "OnWizPageChanged"

    def OnWizPageChanging(self,evt):
        print "OnWizPageChanging"
        if evt.GetDirection():
            try:
                self.convertKDBtoGDB()
            except OSError,info:
                wx.MessageBox(str(info), "Conversion ERROR")

    """
    Convert KDB into GDB.
    English names are used for all teams (from teams.txt file)
    """
    def convertKDBtoGDB(self):
        kdbPath = self.dirs["KDB"]
        gdbPath = self.dirs["GDB"]

        # read team names
        teamMap = {}
        i = open("converter.txt")
        for line in i: 
            tok = line.split(",")
            try: teamMap[int(tok[0])] = tok[1].strip()
            except IndexError: pass
        i.close()

        # create GDB folder
        if os.path.exists("%s\\GDB" % gdbPath):
            # need to backup existing
            i, done = 0, False
            while not done:
                i = i+1
                done = not os.path.exists("%s\\GDB.bak%d" % (gdbPath,i))
            # rename existing folder
            os.rename("%s\\GDB" % gdbPath, "%s\\GDB.bak%d" % (gdbPath,i))

        gdbPath = "%s\\GDB\\uni" % gdbPath
        mkdirs(gdbPath)
        gdbTeams = []

        names = {
            0:"ga/all",3:"ga/numbers",4:"ga/font",
            5:"gb/all",8:"gb/numbers",9:"gb/font",
            10:"pa/shirt",11:"pa/shorts",12:"pa/socks",13:"pa/numbers",14:"pa/font",
            15:"pb/shirt",16:"pb/shorts",17:"pb/socks",18:"pb/numbers",19:"pb/font",
        }
        allnames = { 10:"pa/all", 15:"pb/all" }
        suffixes = [ "-palA", "-palB", "-gloves", "-mip1", "-mip2" ]

        # enumerate KDB dirs
        FIRST_ID = 4576
        dirs = [item for item in os.listdir(kdbPath) if os.path.isdir("%s/%s" % (kdbPath,item))]
        
        # create progress bar dialog
        count = 0
        dlg = wx.ProgressDialog("Conversion progress monitor",
                   "Converting KDB to GDB...",
                   maximum = len(dirs),
                   parent=self,
                   style = wx.PD_CAN_ABORT
                    | wx.PD_APP_MODAL
                    | wx.PD_ELAPSED_TIME
                    #| wx.PD_ESTIMATED_TIME
                    | wx.PD_REMAINING_TIME
                    )

        for dir in dirs:
            try:
                try: id = int(dir)
                except: pass # not a team folder --> skip
                else:
                    teamId = (id - 4576) / 20
                    residue = (id - 4576) % 20
                    if residue == 0 and teamMap.has_key(teamId): 
                        print "(%s) %s: %s" % (id, teamId, teamMap[teamId])

                        gdbTeams.append(teamId)
                        # create corresponding folders in GDB
                        mkdirs("%s/%s/ga" % (gdbPath, teamMap[teamId]))
                        mkdirs("%s/%s/gb" % (gdbPath, teamMap[teamId]))
                        mkdirs("%s/%s/pa" % (gdbPath, teamMap[teamId]))
                        mkdirs("%s/%s/pb" % (gdbPath, teamMap[teamId]))

                        # dictionaries for attributes
                        config = {"ga":{}, "gb":{}, "pa":{}, "pb":{}}

                        teamDir = "%s/%s" % (kdbPath,dir)
                        files = [item for item in os.listdir(teamDir) if os.path.isfile("%s/%s" % (teamDir,item))]
                        for filename in files:
                            file, ext = os.path.splitext(filename)
                            # check suffix
                            suffix = ""
                            for s in suffixes:
                                if file.endswith(s): 
                                    suffix = s
                                    file = file[:-len(suffix)]
                            # determine what file this is
                            try: fid = int(file)
                            except: pass # unknown type --> skip
                            else:
                                ftype = (fid - 4576) % 20
                                try: gdbFile = "%s%s%s" % (names[ftype], suffix, ext)
                                except: pass # unknown number-id
                                else:
                                    # check if this is an all-in-one kit
                                    if allnames.has_key(ftype):
                                        # apply mask
                                        img = wx.Bitmap("%s/%s" % (teamDir,filename)).ConvertToImage()
                                        if not img.HasAlpha(): img.InitAlpha()
                                        # check 4 pixels
                                        if suffix == "-mip1":
                                            t0 = img.GetAlpha(50,75)
                                            t1 = img.GetAlpha(50,78)
                                            t2 = img.GetAlpha(60,78)
                                            t3 = img.GetAlpha(60,75)
                                        elif suffix == "-mip2":
                                            t0 = img.GetAlpha(25,40)
                                            t1 = img.GetAlpha(25,42)
                                            t2 = img.GetAlpha(30,42)
                                            t3 = img.GetAlpha(30,40)
                                        else:
                                            t0 = img.GetAlpha(100,150)
                                            t1 = img.GetAlpha(100,155)
                                            t2 = img.GetAlpha(120,155)
                                            t3 = img.GetAlpha(120,150)
                                        if t0 + t1 + t2 + t3 > 0:
                                            # all-in-one
                                            gdbFile = "%s%s%s" % (allnames[ftype], suffix, ext)

                                    copyFile("%s/%s" % (teamDir,filename), "%s/%s/%s" % (gdbPath,teamMap[teamId],gdbFile))
                                    print "created %s/%s/%s" % (gdbPath,teamMap[teamId],gdbFile)
                                    
                                    # update config dictionaries
                                    kitKey,piece = names[ftype].split("/")
                                    if piece == "numbers" and suffix == "":
                                        config[kitKey]["numbers"] = "%s%s" % (piece,ext)
                                    elif piece == "numbers" and suffix == "-palA":
                                        config[kitKey]["shorts.num-pal.%sa" % kitKey[0]] = "%s-palA%s" % (piece,ext)
                                    elif piece == "numbers" and suffix == "-palB":
                                        config[kitKey]["shorts.num-pal.%sb" % kitKey[0]] = "%s-palB%s" % (piece,ext)

                        # read attrib.cfg
                        readFromAttrib(config, "%s/attrib.cfg" % teamDir)

                        # write config.txt files
                        for key in config.keys():
                            cfg = config[key]
                            if len(cfg.keys())>0:
                                writeConfig(cfg, "%s/%s/%s/config.txt" % (gdbPath,teamMap[teamId],key))

                        # update progress bar
                        dlg.Update(count, "KDB folder (%s) converted." % dir)
            except:
                print "failed to convert team from folder %s. Skipping it." % dir

            count += 1
            dlg.Update(count)

        # create map.txt file
        map = open("%s/map.txt" % gdbPath,"wt")
        print >>map, "# Team folders configuration file"
        print >>map, "# (auto-generated by KDB->GDB converter)"
        print >>map, ""
        for team in gdbTeams:
            print >>map, "%d,\"%s\"" % (team, teamMap[team])
        map.close()

        dlg.Destroy()


#----------------------------------------------------------------------

def copyFile(src, dest):
    i = open(os.path.normpath(src),"rb")
    o = open(os.path.normpath(dest), "wb")
    o.write(i.read())
    o.close()
    i.close()

def mkdirs(dirspec):
    try: os.makedirs(dirspec)
    except OSError: pass

def writeConfig(cfg, filename):
    o = open(os.path.normpath(filename), "wt")
    print >>o, "# Kit attributes file"
    print >>o, "# (auto-generated by KDB->GDB converter)"
    print >>o, ""
    keys = cfg.keys()
    keys.sort()
    for key in keys:
        if key == "numbers" or key.startswith("shorts.num-pal"):
            print >>o, "%s = \"%s\"" % (key, cfg[key])
        else:
            print >>o, "%s = %s" % (key, cfg[key])

def readFromAttrib(config, filename):
    try: i = open(os.path.normpath(filename))
    except IOError: pass
    else:
        section = ""
        for line in i:
            # strip off comments
            comm = line.find("#")
            if comm > -1:
                line = line[:comm]

            # strip off any remaining white space
            line = line.strip()
            if len(line) == 0:
                continue

            # check for start of a section
            if line[0]=="[" and line[-1]=="]":
                section = line[1:-1]
            else:
                tok = [s.strip() for s in line.split("=")]
                try: cfg = config[section]
                except KeyError: pass # unknown section
                else:
                    cfg[tok[0]] = tok[1]

        i.close()
 



#----------------------------------------------------------------------

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        #b = wx.Button(self, -1, "Run Simple Wizard", pos=(50, 50))
        #self.Bind(wx.EVT_BUTTON, self.OnRunSimpleWizard, b)

        #self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        #self.Bind(wiz.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        #self.Bind(wiz.EVT_WIZARD_CANCEL, self.OnWizCancel)


    def OnWizPageChanged(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        self.log.write("OnWizPageChanged: %s, %s\n" % (dir, page.__class__))


    def OnWizPageChanging(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        self.log.write("OnWizPageChanging: %s, %s\n" % (dir, page.__class__))


    def OnWizCancel(self, evt):
        page = evt.GetPage()
        self.log.write("OnWizCancel: %s\n" % page.__class__)

        # Show how to prevent cancelling of the wizard.  The
        # other events can be Veto'd too.
        if page is self.page1:
            wx.MessageBox("Cancelling on the first page has been prevented.", "Sorry")
            evt.Veto()

    def OnWizFinished(self, evt):
        self.log.write("OnWizFinished\n")
        
#----------------------------------------------------------------------

def RunConverterWizard(frame, bitmap):
    frame.dirs = {"KDB":"C:\\", "GDB":"C:\\"}

    # Create the wizard and the pages
    wizard = wiz.Wizard(frame, -1, "KDB-->GDB Converter", bitmap)
    page1 = TitledPage(wizard, "KDB --> GDB")
    page2 = PageChooseKDB(wizard, "Choose KDB folder", frame.dirs)
    page3 = PageChooseGDB(wizard, "Choose GDB location", frame.dirs)
    page4 = PageConfirm(wizard, "Confirm inputs", frame.dirs)
    page5 = TitledPage(wizard, "Conversion finished")
    frame.page1 = page1

    page1.sizer.Add(wx.StaticText(page1, -1, """
This wizard will create a new GDB from an existing KDB (the
older-format kits database used by Kitserver 5.0). The converter
will use English names for all teams, so if you want to change 
those, you can do it after the conversion is done.

NOTE: If you specify a destination folder where you already 
have an existing GDB, the converter will backup your current 
GDB, so nothing will be lost or overwritten. 
Press "Next" to continue."""))
    wizard.FitToPage(page1)
    page5.sizer.Add(wx.StaticText(page5, -1, """
KDB->GDB conversion completed successfully.
You can now use your new GDB with Kitserver 5.1.

Press "Finish" to exit the converter, and return
back to GDB Manager.
"""))

    # Use the convenience Chain function to connect the pages
    wiz.WizardPageSimple_Chain(page1, page2)
    wiz.WizardPageSimple_Chain(page2, page3)
    wiz.WizardPageSimple_Chain(page3, page4)
    wiz.WizardPageSimple_Chain(page4, page5)

    return wizard.RunWizard(page1)


