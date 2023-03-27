
import sys, time, math, os, os.path

import wx
_ = wx.GetTranslation
import wx.propgrid as wxpg

class PropertyGridPanel( wx.Panel ):

    def __init__( self, parent, log ):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.log = log
        self.active_model = None
        self.panel = panel = wx.Panel(self, wx.ID_ANY)
        topsizer = wx.BoxSizer(wx.VERTICAL)

        # Difference between using PropertyGridManager vs PropertyGrid is that
        # the manager supports multiple pages and a description box.
        self.pg = pg = wxpg.PropertyGrid(panel,
                        style=wxpg.PG_SPLITTER_AUTO_CENTER |
                              #wxpg.PG_AUTO_SORT |
                              wxpg.PG_TOOLBAR)

        pg.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)

        pg.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        pg.Bind( wxpg.EVT_PG_PAGE_CHANGED, self.OnPropGridPageChange )
        pg.Bind( wxpg.EVT_PG_SELECTED, self.OnPropGridSelect )
        pg.Bind( wxpg.EVT_PG_RIGHT_CLICK, self.OnPropGridRightClick )

        topsizer.Add(pg, 1, wx.EXPAND)
       

        panel.SetSizer(topsizer)
        topsizer.SetSizeHints(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def OnPropGridChange(self, event):
        p = event.GetProperty()
        if p:
            self.active_model.updateProperty(p)
            #print('%s changed to "%s"\n' % (p.GetName(),p.GetValueAsString()))

    def OnPropGridSelect(self, event):
        p = event.GetProperty()
        #print p

    def OnDeleteProperty(self, event):
        p = self.pg.GetSelectedProperty()
        if p:
            self.pg.DeleteProperty(p)
        else:
            wx.MessageBox("First select a property to delete")

    def OnReserved(self, event):
        pass

    def setModel(self,model):
        self.PopulateProperties(model)
        self.active_model = model
        
    def assignProject(self,active_project):
        active_project.properties_tree = self
    
    def PopulateProperties(self,model):
        self.pg.Clear()
        categories = model.getPropertyCategories()
        for property in model.getProperties():
            if property.getCategory() == None:
                p = property.createwxproperty()
                self.pg.Append(p)
                
        #add the category items
        for category in categories:
            self.pg.Append(wxpg.PropertyCategory(category))
            for property in model.getProperties():
                if property.getCategory() == category:
                    self.pg.Append( property.createwxproperty() )
                    
            
    def OnPropGridRightClick(self, event):
        p = event.GetProperty()


    def OnPropGridPageChange(self, event):
        index = self.pg.GetSelectedPage()






