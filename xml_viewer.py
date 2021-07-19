import wx
import wx.stc as stc

class XmlSTC(stc.StyledTextCtrl):
    """
    Class to view the raw text of an XML file.
    """
    #TODO: My version displays the whole xml file text on one line, rather than providing a new line for every xml node begin and end... Fix this.
    def __init__(self, parent: wx.Window, xml_file: str) -> None:
        """
        Basic constructor of XML Styled Text Control

        :param parent: The parent window for this object
        :type parent: wx.Window
        :param xml_file: The xml file to display
        :type xml_file: str
        """
        stc.StyledTextCtrl.__init__(self, parent)

        self.SetLexer(stc.STC_LEX_XML)
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "size:12,face:Courier New")
        faces = { 'mono' : 'Courier New',
                  'helv' : 'Arial',
                  'size' : 12,
                  }

        # XML styles
        # Default
        self.StyleSetSpec(stc.STC_H_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)

        # Number
        self.StyleSetSpec(stc.STC_H_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # Tag
        self.StyleSetSpec(stc.STC_H_TAG, "fore:#007F7F,bold,size:%(size)d" % faces)
        # Value
        self.StyleSetSpec(stc.STC_H_VALUE, "fore:#7F0000,size:%(size)d" % faces)
        # Attribute
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, "fore:#FF5733,size:%(size)d" % faces)

        # TODO: I think the below means that the XML view will only show the saved version of the XML (not any unsaved changes made)
        with open(xml_file) as fobj:
            text = fobj.read()

        self.SetText(text)


class XmlViewer(wx.Dialog):
    """
    Viewer dialog for displaying the XML styled text control
    """
    
    def __init__(self, xml_file: str) -> None:
        """
        Basic constructor for an XmlViewer dialog

        :param xml_file: The xml file that this XmlViewer will display
        :type xml_file: str
        """
        wx.Dialog.__init__(self, parent=None, title='XML Viewer',
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.xml_view = XmlSTC(self, xml_file)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.xml_view, 1, wx.EXPAND)
        self.SetSizer(sizer)

