import wx
import wx.lib.scrolledpanel as scrolled

from functools import partial
from pubsub import pub
import lxml


class XmlEditorPanel(scrolled.ScrolledPanel):
    """
    The panel in the notebook that allows editing of XML element values
    """

    def __init__(self, parent : wx.Window, page_id : int) -> None:
        """
        Basic Constructor

        :param parent: The parent window of this editor
        :type parent: wx.Window
        :param page_id: The id of the page to be displayed
        :type id: int
        """
        scrolled.ScrolledPanel.__init__(
            self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_id = page_id
        self.widgets = []
        self.label_spacer = None

        pub.subscribe(self.update_ui, f"ui_updater_{self.page_id}")

        self.SetSizer(self.main_sizer)

    def update_ui(self, xml_obj : str) -> None:
        """
        Update the panel's user interface based on the data

        :param xml_obj: The xml objec that is to be updated on the display
        :type xml_obj: lxml.etree
        """
        self.label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.clear()

        tag_lbl = wx.StaticText(self, label='Tags')
        value_lbl = wx.StaticText(self, label='Value')
        self.label_sizer.Add(tag_lbl, 0, wx.ALL, 5)
        self.label_sizer.Add((55, 0))
        self.label_sizer.Add(value_lbl, 0, wx.ALL, 5)
        self.main_sizer.Add(self.label_sizer)

        self.widgets.extend([tag_lbl, value_lbl])

        if xml_obj is not None:
            lbl_size = (75, 25)
            for child in xml_obj.getchildren():
                if child.getchildren():
                    continue
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                tag_txt = wx.StaticText(self, label=child.tag, size=lbl_size)
                sizer.Add(tag_txt, 0, wx.ALL, 5)
                self.widgets.append(tag_txt)

                text = child.text if child.text else ''

                value_txt = wx.TextCtrl(self, value=text)
                value_txt.Bind(wx.EVT_TEXT, partial(self.on_text_change, xml_obj=child))
                sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                self.widgets.append(value_txt)

                self.main_sizer.Add(sizer, 0, wx.EXPAND)
            else:
                if getattr(xml_obj, 'tag') and getattr(xml_obj, 'text'):
                    if xml_obj.getchildren() == []:
                        self.add_single_tag_elements(xml_obj, lbl_size)

                add_node_btn = wx.Button(self, label='Add Node')
                add_node_btn.Bind(wx.EVT_BUTTON, self.on_add_node)
                self.main_sizer.Add(add_node_btn, 0, wx.ALL|wx.CENTER, 5)
                self.widgets.append(add_node_btn)

            self.SetAutoLayout(1)
            self.SetupScrolling()

    def add_single_tag_elements(self, xml_obj : lxml.etree, lbl_size : wx.Size) -> None:
        """
        Adds the single tag elements to the panel

        This function is only called when there should be just one tag / value.
        It creates the objects in place by adding them to self. main_sizer and self.widgets
        As a result, it doesn't return anything
        :param xml_obj: The xml object to display as a single element
        :type xml_obj: lxml.etree
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        tag_txt = wx.StaticText(self, label=xml_obj.tag, size=lbl_size)
        sizer.Add(tag_txt, 0, wx.ALL, 5)
        self.widgets.append(tag_txt)

        value_txt = wx.TextCtrl(self, value=xml_obj.text)
        value_txt.Bind(wx.EVT_TEXT, partial(
            self.on_text_change, xml_obj=xml_obj))
        sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
        self.widgets.append(value_txt)

        self.main_sizer.Add(sizer, 0, wx.EXPAND)

    def clear(self) -> None:
        """
        Clears the widgets from the panel in preparation for an update
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

    def on_text_change(self, event : wx.Event, xml_obj : lxml.etree):
        """
        An event handler that is called when the text changes in the text control.

        This will update the passed in xml object to something
        new.
        :param event: The event that is raised when text is changed on a text box
        :type event: wx.Event
        :param xml_obj: The xml object that has been changed
        :type xml_obj: lxml.etree
        """
        # TODO: This needs to change in order for tags to be able to be changed as well as values.
        xml_obj.text = event.GetString()
        pub.sendMessage(f"on_change_{self.page_id}",
                        event=None)

    def on_add_node(self, event):
        """
        Event handler that adds an XML node using pubsub
        :param event: The event called on adding a node
        :type event: wx.Event
        """
        pub.sendMessage(f"add_node_{self.page_id}")
