import wx
import wx.adv
from wx.adv import Wizard as wiz
import dvtfront_py.ui.images
from wx.adv import WizardPage, WizardPageSimple
from dvtfront_py.ui.progressdlg import ProgressObserver
class AddOdxWizard(wiz):
    def __init__(self,window,model):
        wiz.__init__(self, window, -1, "Simple Wizard", dvtfront_py.ui.images.wizard.GetBitmap())
        page1 = TitledPage(self, "Add ODX File")
        self.page1 = page1

        #bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText2 = wx.StaticText( page1, wx.ID_ANY, "Odx File", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        self.m_staticText2.SetFont( wx.Font( 9, 74, 90, 92, False, "Verdana" ) )
        
        fgSizer1.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_dirPicker1 = wx.FilePickerCtrl( page1, wx.ID_ANY, wx.EmptyString, "Select a folder", "ODX File (*.odx)|*.odx", wx.DefaultPosition, wx.Size( 200,-1 ), wx.DIRP_DEFAULT_STYLE )
        fgSizer1.Add( self.m_dirPicker1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        
        self.m_staticText1 = wx.StaticText( page1, wx.ID_ANY, "Variant Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        self.m_staticText1.SetFont( wx.Font( 9, 74, 90, 92, False, "Verdana" ) )
        
        fgSizer1.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_variantchooser = wx.Choice( page1, wx.ID_ANY, wx.DefaultPosition, wx.Size( 200,-1 ), choices=[] )
        fgSizer1.Add( self.m_variantchooser, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        

        
        
        #bSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )        

        page1.sizer.Add(fgSizer1)
        self.FitToPage(page1)
       

        # Use the convenience Chain function to connect the pages
        #wiz.WizardPageSimple.Chain(page1,None)
        
        self.GetPageAreaSizer().Add(page1)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        self.Bind(wx.adv.EVT_WIZARD_CANCEL, self.OnWizCancel)
        self.Bind(wx.EVT_FILEPICKER_CHANGED,self.onPicerChanged,self.m_dirPicker1)
        
        self.model = model
        self.cid = self.model.getRoot().getCID()
        
        
        
    def onPicerChanged(self,evt):
        processdlg = ProgressObserver(self,"Load ODX","Parsing the odx")
        processdlg.notify()
        variantlist = self.cid.parseOdx(self.m_dirPicker1.GetPath())
        self.m_variantchooser.Clear()
        self.m_variantchooser.AppendItems(variantlist)
        processdlg.finish()

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
        page = evt.GetPage()

        # Show how to prevent cancelling of the wizard.  The
        # other events can be Veto'd too.
        if page is self.page1:
            wx.MessageBox("Cancelling on the first page has been prevented.", "Sorry")
            evt.Veto()


    def OnWizFinished(self, evt):
        
        if self.cid!=None and self.m_variantchooser.GetSelection()!=-1:
            return True
        
    def getCID(self):
        return self.cid
    
    def getVariant(self):
        return self.m_variantchooser.GetStringSelection()
    
    def getPath(self):
        return self.m_dirPicker1.GetPath()


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