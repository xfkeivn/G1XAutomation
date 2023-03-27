import wx
from wx.adv import Wizard,WizardPageSimple
import sim_desk.ui.images


class NewProjectWizard(Wizard):

    def __init__(self, window):
        Wizard.__init__(self, window, -1, "G1X Project Wizard")
        page1 = TitledPage(self, "Create New Project")
        self.page1 = page1

        # bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        
        self.m_staticText1 = wx.StaticText(page1, wx.ID_ANY, "Project Name", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        self.m_staticText1.SetFont(wx.Font(9, 74, 90, 92, False, "Verdana"))
        
        fgSizer1.Add(self.m_staticText1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.m_textCtrl1 = wx.TextCtrl(page1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1), 0)
        fgSizer1.Add(self.m_textCtrl1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.m_staticText2 = wx.StaticText(page1, wx.ID_ANY, "Project Location", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        self.m_staticText2.SetFont(wx.Font(9, 74, 90, 92, False, "Verdana"))
        
        fgSizer1.Add(self.m_staticText2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.m_dirPicker1 = wx.DirPickerCtrl(page1, wx.ID_ANY, wx.EmptyString, "Select a folder", wx.DefaultPosition, wx.Size(200, -1), wx.DIRP_DEFAULT_STYLE)
        fgSizer1.Add(self.m_dirPicker1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # bSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )        

        page1.sizer.Add(fgSizer1)
        self.FitToPage(page1)

        # Use the convenience Chain function to connect the pages
        # wiz.WizardPageSimple.Chain(page1,None)
        
        self.GetPageAreaSizer().Add(page1)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        self.Bind(wx.adv.EVT_WIZARD_CANCEL, self.OnWizCancel)
        self.Bind(wx.adv.EVT_WIZARD_FINISHED, self.OnWizFinished)

    def run(self):
        return self.RunWizard(self.page1)
    
    def OnWizPageChanged(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        # self.log.write("OnWizPageChanged: %s, %s\n" % (dir, page.__class__))

    def OnWizPageChanging(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()

    def OnWizCancel(self, evt):
        return True

    def OnWizFinished(self, evt):
        return True

    def getProjectName(self):
        return self.m_textCtrl1.GetValue()
    
    def getProjectDir(self):
        return self.m_dirPicker1.GetPath()

#----------------------------------------------------------------------


class TitledPage(WizardPageSimple):

    def __init__(self, parent, title):
        WizardPageSimple.__init__(self, parent)
        self.sizer = self.makePageTitle(self, title)

    def makePageTitle(self, wizPg, title):
        sizer = wx.BoxSizer(wx.VERTICAL)
        wizPg.SetSizer(sizer)
        title = wx.StaticText(wizPg, -1, title)
        title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND | wx.ALL, 5)
        return sizer
