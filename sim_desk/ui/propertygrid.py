
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
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # Difference between using PropertyGridManager vs PropertyGrid is that
        # the manager supports multiple pages and a description box.
        self.pg = pg = wxpg.PropertyGrid(panel,
                        style=wxpg.PG_SPLITTER_AUTO_CENTER |
                              #wxpg.PG_AUTO_SORT |
                              wxpg.PG_TOOLBAR)
        pg.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        pg.Bind(wxpg.EVT_PG_CHANGED, self.on_prop_grid_change)
        pg.Bind(wxpg.EVT_PG_PAGE_CHANGED, self.on_prop_grid_page_change)
        pg.Bind(wxpg.EVT_PG_SELECTED, self.on_prop_grid_select)
        pg.Bind(wxpg.EVT_PG_RIGHT_CLICK, self.on_prop_grid_right_click)
        top_sizer.Add(pg, 1, wx.EXPAND)
        panel.SetSizer(top_sizer)
        top_sizer.SetSizeHints(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def on_prop_grid_change(self, event):
        p = event.GetProperty()
        if p:
            self.active_model.updateProperty(p)

    def on_prop_grid_select(self, event):
        p = event.GetProperty()

    def on_delete_property(self, event):
        p = self.pg.GetSelectedProperty()
        if p:
            self.pg.DeleteProperty(p)
        else:
            wx.MessageBox("First select a property to delete")

    def on_reserved(self, event):
        pass

    def set_model(self, model):
        self.populate_properties(model)
        self.active_model = model
        
    def assign_project(self, active_project):
        active_project.properties_tree = self
    
    def populate_properties(self, model):
        self.pg.Clear()
        categories = model.getPropertyCategories()
        for property in model.getProperties():
            if property.getCategory() is None:
                p = property.createwxproperty()
                self.pg.Append(p)
        for category in categories:
            self.pg.Append(wxpg.PropertyCategory(category))
            for property in model.getProperties():
                if property.getCategory() == category:
                    self.pg.Append( property.createwxproperty() )

    def on_prop_grid_right_click(self, event):
        p = event.GetProperty()

    def on_prop_grid_page_change(self, event):
        index = self.pg.GetSelectedPage()






