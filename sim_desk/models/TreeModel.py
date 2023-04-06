import sim_desk.ui.images
from wx.lib.newevent import NewEvent
import wx

IMAGE_STATE_EXPAND  = 0
IMAGE_STATE_COLLAPSE = 1
IMAGE_STATE_NORMAL = 2
TREEMODEL_STATUS_RUNTIME = 0
TREEMODEL_STATUS_NORMAL = 1

(AddToTreeEvent, EVT_ADD_TO_TREE_EVENT) = NewEvent()
(RemoveFromTreeEvent, EVT_REMOVE_FROM_TREE_EVENT) = NewEvent()
(ModelSelectChangeEvent, EVT_MODEL_SELECT_CHANGE_EVENT) = NewEvent()
(DirtyStateChangedEvent, EVT_MODEL_DIRTYSTATE_CHANGE_EVENT) = NewEvent()
(UpdateTreeItemImage,EVT_UPDATE_TREE_ITEM_IMAGE) = NewEvent()
(UpdateTreeItemLabel,EVT_UPDATE_TREE_ITEM_LABEL) = NewEvent()
(AddControlPanel,EVT_ADD_CONTROL_PANEL) = NewEvent()
(AUIManagerUpdate,EVT_AUI_MANAGER_UPDATE) = NewEvent()


class TreeAction():
    def __init__(self,name,eventid,callablefunc,image = None):
        self.name = name
        self.image = image
        self.eventid = eventid
        self.callable = callablefunc


class TreeModel():
    def __init__(self,parent,tag_name=None):
        self.children_models=[]
        self.parent = parent
        self.project_tree = None
        self.tag_name = tag_name
        self.label = tag_name
        self.tree_action_list=[]
        self.is_Dirty = False
        self.properties = []
        self.image = None
        self.properties_tree = None
        self.tree_item = None
        self.__console = None
        self.status = TREEMODEL_STATUS_NORMAL
        self.json_element = None
        
    def setTreeItem(self,treeitem):
        self.tree_item = treeitem
        
    def addProperties(self,commonproperty):
        self.properties.append(commonproperty)
        return commonproperty
    
    def getPropertyByName(self,propertyname):
        for p in self.properties:
            if p.getName() == propertyname:
                return p
        return None
    
    def __getPropertyBywxprop(self,wxprop):
        for p in self.properties:
            #print p.getWxProperty(),wxprop
            if str(p.getWxProperty()) == str(wxprop):
                return p
        return None

    def getPropertyBywxprop(self,wxprop):
        return self.__getPropertyBywxprop(wxprop)
    
    def updateProperty(self,wxprop):
        prop = self.__getPropertyBywxprop(wxprop)
        if prop:
            prop.setStringValue(wxprop.GetValueAsString())
            self.setDirty()
        return prop
        
    def getProperties(self):
        return self.properties
    
    def getPropertyCategories(self):
        categories=[]
        for prop in self.properties:
            if prop.getCategory() is not None:
                if prop.getCategory() not in categories:
                    categories.append(prop.getCategory())
        return categories
                

    def getRoot(self):
        if self.parent is None:
            return self
        else:
            return self.parent.getRoot()   

    def getProject_Tree(self):
        if self.project_tree is not None:
            return self.project_tree
        else:
            if self.parent is None:
                return None
            else:
                return self.parent.getProject_Tree()
    
    def getProperties_Tree(self):
        if self.properties_tree is not None:
            return self.properties_tree
        else:
            if self.parent is None:
                return None
            else:
                return self.parent.getProperties_Tree()    

    @property       
    def console(self):
        if self.__console is not None:
            return self.__console
        else:
            if self.parent is None:
                return None
            else:
                self.__console = self.parent.console 
                return self.__console

    @console.setter
    def console(self, value):
        self._console = value
            

    def getModelParent(self):
        return self.parent

    def setModelLabel(self,label_str):
        self.label = label_str
        uti= UpdateTreeItemLabel(label = label_str,model=self)
        if self.getProject_Tree() is not None:
            wx.PostEvent(self.getProject_Tree(),uti)
        
    def to_json(self):
        json_result = {}

        json_result.setdefault('properties', {})
        if len(self.children_models) >= 1:
            json_result.setdefault('sub_models', {})

        if self.children_models is not None and len(self.children_models) >= 1:
            for model in self.children_models:
                json_result['sub_models'][model.label] = model.to_json()
        if self.properties is not None and len(self.properties) >= 1:
            for prop in self.properties:
                json_result['properties'][prop.label] = prop.to_json()
        return json_result

    def from_json(self,element):
        sub_models = element.get('sub_models',{})
        properties = element.get('properties',{})

        for modelname, childelement in sub_models.items():
            childmodel = self.getChildrenByLabel(modelname)
            if len(childmodel) == 1:
                childmodel[0].from_json(childelement)
        for properyname,propmodel in properties.items():
            prop = self.getPropertyByName(properyname)
            if prop is not None:
                prop.from_json(propmodel)
            else:
                pass


    def getLabel(self):
        return self.label
    
    def getTagName(self):
        return self.tag_name
    
    def getImage(self):
        return self.image
    
    def setImage(self,image):
        self.image = image
        uti= UpdateTreeItemImage(image = self.image,model=self)
        if self.getProject_Tree() is not None:
            wx.PostEvent(self.getProject_Tree(),uti)
    
    
    def getChildByTag(self,tagname):
        for child in self.children_models:
            if  child.getTagName() == tagname:
                return child
        return None
    
    def getChildrenByLabel(self,label):
        children=[]
        for child in self.children_models:
            if  child.getLabel() == label:
                children.append(child)      
        return children  
    
    def addChild(self,childmodel, addtotree= True):
        self.children_models.append(childmodel)
        if addtotree and self.getProject_Tree() is not None:
            add_evt = AddToTreeEvent(model_to_add=childmodel,parent_model = self)
            wx.PostEvent(self.getProject_Tree(),add_evt)
        self.setDirty()
           
    def removeChild(self,childmodel,remove_from_tree=True):
        if childmodel in self.children_models:
            self.children_models.remove(childmodel)
            if remove_from_tree and self.getProject_Tree()!=None:
                rm_evt = RemoveFromTreeEvent(model_to_remove=childmodel)
                wx.PostEvent(self.getProject_Tree(),rm_evt)
        self.setDirty()

    def remove(self):
        self.parent.removeChild(self)
        self.setDirty()
        
    def getModelChildren(self):
        return self.children_models
    
    def getActions(self):
        return self.tree_action_list
    
    def isDirty(self):
        return self.getRoot().is_Dirty


    def setDirty(self,flag= True):
        self.getRoot().is_Dirty = flag
        dsc_evt= DirtyStateChangedEvent(dirtystate = flag)
        if self.getProject_Tree():
            wx.PostEvent(self.getProject_Tree().GetParent(),dsc_evt)
        
    def close(self):
        for child in self.children_models:
            child.close()
    
    def onActivate(self):
        if self.getProject_Tree()!=None:
            self.getProperties_Tree().setModel(self)

        
    def set_model_status(self,modelstatus):
        self.status = modelstatus
        for child in self.getModelChildren():
            child.set_model_status(modelstatus)
        
class GenericContainer(TreeModel):
    def __init__(self,parent,name):
        TreeModel.__init__(self, parent, name)
        self.label= name
    
    def getImage(self):
        return sim_desk.ui.images.folder_collapse


        