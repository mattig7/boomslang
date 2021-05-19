import wx

from edit_dialog import EditDialog
from pubsub import pub


class AttributeDialog(EditDialog):
    """
    Dialog class for adding attributes to nodes
    """

    def on_save(self, event : wx.Event) -> None:
        """
        Event handler that is called when the Save button is
        pressed.

        Updates the XML object with the new node element and
        tells the UI to update to display the new element
        before destroying the dialog
        :param event: The event called to save the dialog.
        :type event: wx.Event
        """
        attr = self.value_one.GetValue()
        value = self.value_two.GetValue()
        if attr:
            self.xml_obj.attrib[attr] = value
            pub.sendMessage(f"ui_updater_{self.page_id}", xml_obj=self.xml_obj)
            pub.sendMessage(f"on_change_{self.page_id}", event=None)
        else:
            # TODO - Show a dialog telling the user that there is no attr to save
            raise NotImplemented

        self.Close()
