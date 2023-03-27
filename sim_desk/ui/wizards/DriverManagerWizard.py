import wx
from wx.adv import  Wizard
from wx.adv import WizardPageSimple
import sim_desk.ui.images
import sys
from sim_desk.mgr.drivermanager import DriverManager
from sim_desk.mgr.appconfig import AppConfig
from devicedriver import genericdriver


class DriverManagerWizard(Wizard):

    def __init__(self, window):
        Wizard.__init__(self, window, -1, "Driver Manager", dvtfront_py.ui.images.wizard.GetBitmap())
        page1 = TitledPage(self, "Driver Manager Page")
        self.page1 = page1

        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        
        self.driverlist = wx.ListCtrl(page1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ALIGN_LEFT | wx.LC_REPORT | wx.LC_SINGLE_SEL)
        
        self.driverlist.InsertColumn(0, "Name")
        self.driverlist.InsertColumn(1, "Ver",)
        self.driverlist.InsertColumn(2, "Class Name")  
        self.driverlist.InsertColumn(3, "Devices")  
        self.driverlist.SetColumnWidth(0, 150)
        self.driverlist.SetColumnWidth(1, 60)
        self.driverlist.SetColumnWidth(2, 250)
        self.driverlist.SetColumnWidth(3, 60)
        bSizer1.Add(self.driverlist, 1, wx.EXPAND | wx.ALL, 5)
        
        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.m_bpAdd = wx.BitmapButton(page1, wx.ID_ANY, dvtfront_py.ui.images.adddriver.GetBitmap(), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        bSizer2.Add(self.m_bpAdd, 0, wx.ALL, 5)
        
        self.m_bpDelete = wx.BitmapButton(page1, wx.ID_ANY, dvtfront_py.ui.images.removedriver.GetBitmap(), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        bSizer2.Add(self.m_bpDelete, 0, wx.ALL, 5)
        
        self.m_bpDiscover = wx.BitmapButton(page1, wx.ID_ANY, dvtfront_py.ui.images.refreshdriver.GetBitmap(), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        bSizer2.Add(self.m_bpDiscover, 0, wx.ALL, 5) 
        bSizer1.Add(bSizer2, 0, wx.EXPAND, 5)
        self.importerrorlist = wx.TextCtrl(page1)
        self.importerrorlist.SetFont(wx.Font(9, 70, 90, 90, False))
        self.importerrorlist.SetForegroundColour(wx.Colour(255, 0, 0))
        self.importerrorlist.SetSizeHints(100, 100)
        bSizer1.Add(self.importerrorlist, 0, wx.EXPAND, 5)
        page1.sizer.Add(bSizer1, 1, wx.ALL | wx.EXPAND, 5)
        self.FitToPage(page1)

        # Use the convenience Chain function to connect the pages
        # wiz.WizardPageSimple.Chain(page1,None)
        
        self.GetPageAreaSizer().Add(page1)

        self.Bind(Wizard.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(Wizard.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        self.Bind(Wizard.EVT_WIZARD_CANCEL, self.OnWizCancel)
        self.Bind(wx.EVT_BUTTON, self.onAddDriver, self.m_bpAdd)
        self.Bind(wx.EVT_BUTTON, self.onDeleteDriver, self.m_bpDelete)
        self.Bind(wx.EVT_BUTTON, self.onRefreshDriver, self.m_bpDiscover)
        self.driverlist.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnListItemDeselected)
        self.driverlist.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        # self.driverlist.Bind(wx.EVT_KILL_FOCUS,self.onKillFocus)
        self.installed_drivers = []
        
    def onKillFocus(self, evt):
        self.driverlist.SetItemState()
        self.m_bpDelete.Enable(False)
        
    def onAddDriver(self, evt):
        idd = wx.DirDialog(self)
        if wx.ID_OK == idd.ShowModal():
            dirpath = idd.GetPath()
    
    def onDeleteDriver(self, evt):
        driver_to_delete = self.driverlist.GetFirstSelected()

        if driver_to_delete != None:
            dlg = wx.MessageDialog(self, 'Please Confirm to delete ',
                                   'Confirm to delete',
                                   # wx.OK | wx.ICON_INFORMATION
                                   wx.YES_NO | wx.ICON_INFORMATION
                                   )
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                driverclass = self.installed_drivers[driver_to_delete]
                #print sys.modules[driverclass.__module__].__file__
                #print driverclass.__module__
    
    def OnListItemDeselected(self, evt):
     
        if self.driverlist.GetSelectedItemCount() == 0:
            self.m_bpDelete.Enable(False)
    
    def OnListItemSelected(self, evt):
        self.m_bpDelete.Enable(True)
    
    def onRefreshDriver(self, evt):
        self.discoverdrivers()
    
    def discoverdrivers(self):
        # self.driverlist.DeleteRows()
        self.driverlist.DeleteAllItems()
        self.importerrorlist.Clear()
        self.installed_drivers = []
        drivers = DriverManager().discover(AppConfig().getDriverDir())
        index = 0
        for driver in drivers:
            if isinstance(driver, type) and issubclass(driver, genericdriver.GenericDriver):
                self.__add_driver_row(index, driver)
                self.installed_drivers.append(driver)
                index += 1
            else:
                self.importerrorlist.SetValue(self.importerrorlist.GetValue() + str(driver.error) + "\n")
            
    def __add_driver_row(self, row, driver):
        obj = driver()
        index = self.driverlist.InsertStringItem(sys.maxsize, obj.getDriverName())
        self.driverlist.SetStringItem(index, 1, obj.getDriverVersion())
        self.driverlist.SetStringItem(index, 2, driver.__module__ + "." + driver.__name__)
        self.driverlist.SetStringItem(index, 3, str(len(obj.enumerateDevices())))
        
    def run(self):
        self.discoverdrivers()
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
        page = evt.GetPage()

        # Show how to prevent cancelling of the wizard.  The
        # other events can be Veto'd too.
        if page is self.page1:
            wx.MessageBox("Cancelling on the first page has been prevented.", "Sorry")
            evt.Veto()

    def OnWizFinished(self, evt):
        return True

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
