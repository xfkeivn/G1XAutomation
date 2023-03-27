import wx
from  wx.adv import Wizard
import dvtfront_py.ui.images
import  wx.gizmos   as  gizmos
from mgr.AppConfig import AppConfig
from devicedriver.genericdriver import GenericDriver
from mgr.drivermanager import DriverManager
from devicedriver.genericdevice import *
from wx.adv import WizardPage, WizardPageSimple
class AddDeviceWizard(Wizard):
    def __init__(self,window):
        Wizard.__init__(self, window, -1, "Simple Wizard", dvtfront_py.ui.images.wizard.GetBitmap())
        page1 = TitledPage(self, "Add Device")
        self.page1 = page1

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.tree = gizmos.TreeListCtrl(self.page1, -1, style =
                                        wx.TR_DEFAULT_STYLE
                                        #| wx.TR_HAS_BUTTONS
                                        #| wx.TR_TWIST_BUTTONS
                                        #| wx.TR_ROW_LINES
                                        #| wx.TR_COLUMN_LINES
                                        #| wx.TR_NO_LINES
                                        | wx.TR_HIDE_ROOT
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                   )
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.tree.SetImageList(il)
        self.il = il
        # create some columns
        self.tree.AddColumn("Device Name")
        self.tree.AddColumn("Description")
        self.tree.AddColumn("Type")
        self.tree.AddColumn("Added")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 200)
        self.tree.SetColumnWidth(1, 200)
        self.tree.SetColumnWidth(2, 50)
        self.tree.SetColumnWidth(3, 50)
        self.tree.SetSizeHints(500,-1)
        self.root = self.tree.AddRoot("The Root Item")
        self.tree.Expand(self.root)
        #self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        #self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        bSizer1.Add( self.tree, 1, wx.EXPAND|wx.ALL, 5 )        
        page1.sizer.Add(bSizer1,1, wx.EXPAND|wx.ALL,0)
        self.FitToPage(page1)
        # Use the convenience Chain function to connect the pages
        #wiz.WizardPageSimple.Chain(page1,None)
        self.GetPageAreaSizer().Add(page1)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        self.Bind(wx.adv.EVT_WIZARD_CANCEL, self.OnWizCancel)
        self.Bind(wx.adv.EVT_WIZARD_FINISHED,self.OnWizFinished)
        #self.Bind(wx.EVT_FILEPICKER_CHANGED,self.onPicerChanged,self.m_dirPicker1)
        self.discoverdrivers()
        self.selected_device = None

    def discoverdrivers(self):
        #self.driverlist.DeleteRows()
        self.tree.DeleteChildren(self.root)
        drivers = DriverManager().discover(AppConfig().getDriverDir())
        index = 0
        for driver in drivers:
            if isinstance(driver, type) and issubclass(driver, GenericDriver):
                self.__add_driver(index,driver)
                index+=1
            
    def __add_driver(self,row,driver):
        obj =driver()
        child = self.tree.AppendItem(self.root, obj.getDriverName())
        self.tree.SetItemText(child, obj.getDriverVersion(), 1)
        #self.tree.SetItemText(child, driver.__module__ + "."+driver.__name__, 2)
        #self.tree.SetItemText(child, str(len(obj.enumerateDevices())), 3)
        self.tree.SetItemImage(child, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(child, self.fldropenidx, which = wx.TreeItemIcon_Expanded) 
        for device in obj.enumerateDevices():
            last = self.tree.AppendItem(child, device.getDeviceName())
            devicetype = device.getDeviceType()
            self.tree.SetItemText(last, device.getDeviceDescription(), 1)  
            if devicetype == DEVICE_TYPE_REAL:
                self.tree.SetItemText(last, "Real", 2)  
            else:
                self.tree.SetItemText(last, "Virtual", 2) 
            self.tree.SetPyData(last,device)
        
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
        self.selected_device = None


    def OnWizFinished(self, evt):
        sel = self.tree.GetSelection()
        if sel:
            device = self.tree.GetPyData(sel)
            self.selected_device = device
        else:
            self.selected_device = None
            
    def getSelectedDevice(self):
        return self.selected_device
        
        

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
