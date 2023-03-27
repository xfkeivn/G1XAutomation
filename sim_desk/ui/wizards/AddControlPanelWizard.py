import wx
from   wx.adv import Wizard
import dvtfront_py.ui.images
from wx.adv import Wizard,WizardPageSimple

class AddControlPanelWizard(Wizard):
    def __init__(self,window):
        Wizard.__init__(self, window, -1, "Add Control Panel Wizard", dvtfront_py.ui.images.wizard.GetBitmap())
        page1 = TitledPage(self, "Add Control Panel")
        self.page1 = page1

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText1 = wx.StaticText( self.page1, wx.ID_ANY, "Control Panel Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )
        
        self.m_controlpanelname = wx.TextCtrl( self.page1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.m_controlpanelname, 0, wx.ALL, 5 )
        
     

        
    
        page1.sizer.Add(bSizer1,1, wx.EXPAND|wx.ALL,0)
        self.FitToPage(page1)
       

        # Use the convenience Chain function to connect the pages
        #wiz.WizardPageSimple.Chain(page1,None)
        
        self.GetPageAreaSizer().Add(page1)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        self.Bind(wx.adv.EVT_WIZARD_CANCEL, self.OnWizCancel)
        self.Bind(wx.adv.EVT_WIZARD_FINISHED,self.OnWizFinished)
    

    def run(self):
        return self.RunWizard(self.page1)
    
    def OnWizPageChanged(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        #self.log.write("OnWizPageChanged: %s, %s\n" % (dir, page.__class__))


    def OnWizPageChanging(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()


    def OnWizCancel(self, evt):
        return False


    def OnWizFinished(self, evt):
        return True
            
    def getControlPanelName(self):
        return self.m_controlpanelname.GetValue()
        
        

#----------------------------------------------------------------------

class TitledPage(WizardPageSimple):
    def __init__(self, parent, title):
        WizardPageSimple.__init__(self, parent)
        self.sizer = self.makePageTitle(self, title)
    def makePageTitle(self,wizPg, title):
        sizer = wx.BoxSizer(wx.VERTICAL)
        wizPg.SetSizer(sizer)
        title = wx.StaticText(wizPg, -1, title)
        title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
        return sizer
