import wx

from attribute_dialog import AttributeDialog
from functools import partial
from pubsub import pub
import lxml.etree


class State():
    """
    Class for keeping track of the state of the key portion of the attribute.
    This is needed to know what the key was prior to the change that is sent through pubsub.
    """
    # TODO: refactor State class to be a dataclass. Or even a named tuple
    def __init__(self, key : str, val_widget : wx.TextCtrl):
        """
        :param key: The string that is the 'key' of an attribute
        :type key: str
        :param val_widget: The Text Control widget that holds the value for this attribute
        :type val_widget: wx.TextCtrl
        """
        self.current_key = key
        self.previous_key = None
        self.val_widget = val_widget


class AttributeEditorPanel(wx.Panel):
    """
    A class that holds all UI elements for editing
    XML attribute elements. Each XML node can have multiple attributes
    """

    def __init__(self, parent : wx.Window, page_id : int) -> None:
        """
        Constructor

        :param parent: The parent panel for the new AtrributeEditorPanel
        :type parent: wx.Window
        :param page_id: The page id this AttributeEditorPanel relates to.
        :type page_id: int
        """
        wx.Panel.__init__(self, parent)
        self.page_id = page_id
        self.xml_obj = None
        self.widgets = []

        pub.subscribe(self.update_ui, f"ui_updater_{self.page_id}")

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

    def update_ui(self, xml_obj : lxml.etree) -> None:
        """
        Update the user interface to have elements for editing
        XML attributes

        This method is called via pubsub and is linked to 'ui_updater_<page-id>' message
        
        :param xml_obj: The xml_obj that relates to this page id
        :type xml_obj: lxml.etree
        """
        self.clear()
        self.xml_obj = xml_obj

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        attr_lbl = wx.StaticText(self, label='Attribute')
        value_lbl = wx.StaticText(self, label='Value')
        sizer.Add(attr_lbl, 0, wx.ALL, 5)
        sizer.Add((133,0))
        sizer.Add(value_lbl, 0, wx.ALL, 5)
        self.widgets.extend([attr_lbl, value_lbl])

        self.main_sizer.Add(sizer)

        for key in xml_obj.attrib:
            _ = wx.BoxSizer(wx.HORIZONTAL)
            attr_name = wx.TextCtrl(self, value=key)
            _.Add(attr_name, 1, wx.ALL|wx.EXPAND, 5)
            self.widgets.append(attr_name)

            val = str(xml_obj.attrib[key])
            attr_val = wx.TextCtrl(self, value=val)
            _.Add(attr_val, 1, wx.ALL|wx.EXPAND, 5)

            # keep track of the attribute text control's state
            attr_state = State(key, attr_val)

            attr_name.Bind(
                wx.EVT_TEXT, partial(
                    self.on_key_change, state=attr_state))
            attr_val.Bind(
                wx.EVT_TEXT, partial(
                    self.on_val_change,
                    attr=attr_name
                ))

            self.widgets.append(attr_val)
            self.main_sizer.Add(_, 0, wx.EXPAND)
        else:
            add_attr_btn = wx.Button(self, label='Add Attribute')
            add_attr_btn.Bind(wx.EVT_BUTTON, self.on_add_attr)
            self.main_sizer.Add(add_attr_btn, 0, wx.ALL|wx.CENTER, 5)
            self.widgets.append(add_attr_btn)

        self.Layout()

    def on_add_attr(self, event : wx.Event) -> None:
        """
        Event handler to create a dialog for adding a new attribute to a node
        
        :param event: The event called upon adding an attribute.
        :type event: wx.Event
        """
        dlg = AttributeDialog(
            self.xml_obj,
            page_id=self.page_id,
            title = 'Add Attribute',
            label_one = 'Attribute',
            label_two = 'Value'
        )
        dlg.Destroy()

    def clear(self) -> None:
        """
        Clears the panel of widgets
        """
        sizers = {}
        for widget in self.widgets:
            sizer = widget.GetContainingSizer()
            if sizer:
                sizer_id = id(sizer)
                if sizer_id not in sizers:
                    sizers[sizer_id] = sizer
            widget.Destroy()

        for sizer in sizers:
            self.main_sizer.Remove(sizers[sizer])

        self.widgets = []
        self.Layout()

    def on_key_change(self, event : wx.Event, state : State) -> None:
        """
        Event handler that is called on text change in the
        attribute key field

        :param event: The event object triggered on key change
        :type event: wx.Event
        :param state: The State object that gives the changed text control and the previous xml attribute key
        :type state: State
        """
        new_key = event.GetString()
        if new_key not in self.xml_obj.attrib:
            if state.current_key in self.xml_obj.attrib:
                self.xml_obj.attrib.pop(state.current_key)
            self.xml_obj.attrib[new_key] = state.val_widget.GetValue()
            state.previous_key = state.current_key
            state.current_key = new_key
            pub.sendMessage(f"on_change_{self.page_id}", event=None)

    def on_val_change(self, event : wx.Event, attr : wx.TextCtrl) -> None:
        """
        Event handler that is called on text change in the attribute value field.

        :param event: Event that is created upon text change
        :type event: wx.Event
        :param attr: The text Control widget that is being used to change the attribute value.
        :type attr: wx.TextCtrl
        """
        new_val = event.GetString()
        self.xml_obj.attrib[attr.GetValue()] = new_val
        pub.sendMessage(f"on_change_{self.page_id}", event=None)
