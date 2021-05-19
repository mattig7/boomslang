import lxml.etree as ET
import wx

from edit_dialog import EditDialog
from pubsub import pub


class NodeDialog(EditDialog):
    """
    A class for adding nodes to your XML objects.
    """

    def on_save(self, event):
        """
        Event handler that is called when the Save button is
        pressed.

        Updates the XML object with the new node element and
        tells the UI to update to display the new element
        before destroying the dialog
        :param event: The event called when the save button is pressed
        :type event: wx.Event
        """
        element = ET.SubElement(self.xml_obj, self.value_one.GetValue())
        element.text = self.value_two.GetValue()
        pub.sendMessage(f"tree_update_{self.page_id}", xml_obj=element)
        pub.sendMessage(f"on_change_{self.page_id}", event=None)
        self.Close()

if __name__ == '__main__':
    app = wx.App(False)
    dlg = NodeDialog('', title='Test',
                     label_one='Element',
                     label_two='Value')
    dlg.Destroy()
    app.MainLoop()
