import lxml.etree as ET
import os
import sys
import time
import utils
import wx

from boom_attribute_ed import AttributeEditorPanel
from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel
from pubsub import pub

class NewPage(wx.Panel):
    """
    Create a new page for an opened XML document. This is the top-level widget for the majority of the application
    """
    # TODO: Clean this method up using the pathlib.Path module (edit all other files that use os.path as well)
    def __init__(self, parent : wx.Window, xml_path : str, size : wx.Size, opened_files : list) -> None:
        """
        Constructor

        :param parent: The parent of this :class NewPage: widget
        :type parent: wx.Window
        :param xml_path: The file system path to the xml file being opened
        :type xml_path: str
        :param size: The initial size of the created :class NewPage: widget
        :type size: wx.Size
        :param opened_files: The list of files that are opened in this instance of boomslang.
        :type opened_files: list
        """
        wx.Panel.__init__(self, parent)
        self.page_id = id(self)
        self.xml_root = None
        self.size = size
        self.opened_files = opened_files
        self.current_file = xml_path
        self.title = os.path.basename(xml_path)
        
        self.app_location = os.path.dirname(os.path.abspath( sys.argv[0] ))

        self.tmp_location = os.path.join(self.app_location, 'drafts')

        pub.subscribe(self.save, f"save_{self.page_id}")
        pub.subscribe(self.auto_save, f"on_change_{self.page_id}")

        self.parse_xml(xml_path)

        current_time = time.strftime('%Y-%m-%d.%H.%M.%S', time.localtime())
        self.full_tmp_path = os.path.join(
            self.tmp_location,
            current_time + '-' + os.path.basename(xml_path))

        if not os.path.exists(self.tmp_location):
            try:
                os.makedirs(self.tmp_location)
            except IOError:
                raise IOError('Unable to create file at {}'.format(
                    self.tmp_location))

        if self.xml_root is not None:
            self.create_editor()

    def create_editor(self) -> None:
        """
        Create the XML editor widgets

        A helper method that creates the various sub-widgets required to display an editor page.
        """
        page_sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self)
        tree_panel = BoomTreePanel(splitter, self.xml_root, self.page_id)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        attribute_panel = AttributeEditorPanel(
            xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(attribute_panel, 'Attributes')

        splitter.SplitVertically(tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(self.size[0] / 2)
        page_sizer.Add(splitter, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(page_sizer)
        self.Layout()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def auto_save(self, event : wx.Event) -> None:
        """
        Event handler that is called via pubsub to save the
        current version of the XML to disk in a temporary location

        :param event: The event that is called to auto save this editor page.
        :type event: wx.Event
        """
        self.xml_tree.write(self.full_tmp_path)
        pub.sendMessage('on_change_status', save_path=self.full_tmp_path)

    def parse_xml(self, xml_path : str):
        """
        Parses the XML from the file that is passed in

        :param xml_path: The string file system path to the xml file to be opened
        :type xml_path: str
        """
        self.current_directory = os.path.dirname(xml_path)
        try:
            self.xml_tree = ET.parse(xml_path)
        except IOError:
            print('Bad file')
            return
        except Exception as e:
            print('Really bad error')
            print(e)
            return

        self.xml_root = self.xml_tree.getroot()

    def save(self, location : str = None):
        """
        Save the XML to disk

        :param location: The string file system path (including file name and suffix) to save the current xml file to.
        :type location: str
        """
        if not location:
            path = utils.save_file(self)
        else:
            path = location

        if path:
            if '.xml' not in path:
                path += '.xml'

            # Save the xml
            self.xml_tree.write(path)
            self.changed = False

    def on_close(self, event):
        """
        Event handler that is called when the panel is being closed

        :param event: The event that is called on close of this editor
        :type event: wx.Event
        """
        if self.current_file in self.opened_files:
            self.opened_files.remove(self.current_file)

        if os.path.exists(self.full_tmp_path):
            try:
                os.remove(self.full_tmp_path)
            except IOError:
                print(f"Unable to delete file: {self.full_tmp_path}")
