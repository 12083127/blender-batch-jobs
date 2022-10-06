

import wx
import wx.dataview

from appmanager import AppList, AppSettings


class BBJGUI(wx.App):
    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super(BBJGUI, self).__init__(
            redirect, filename, useBestVisual, clearSigInt)

    def OnInit(self):
        _window_pos = AppSettings.window_position
        _window_size = AppSettings.window_size
        frame = BBJFrame(
            parent=None, title="Blender Batch Jobs", pos=_window_pos, size=_window_size)
        frame.SetMinSize((640, 480))
        frame.Show()
        return True

    def OnExit(self):
        # save stuff
        print("Quitting app")
        return super().OnExit()


class AppPicker(wx.Choice):
    def __init__(self, parent):
        super(AppPicker, self).__init__(
            parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.SetToolTip("Pick default Blender installation")
        self.Bind(wx.EVT_CHOICE, self.__on_choice)
        self.update()

    def update(self):
        self.Clear()
        if AppList.get():
            for app in AppList.get():
                self.Append(app.__str__())
            self.SetSelection(AppList.get_active_installation_index())
        self.SetSize(self.GetBestSize())
        self.Parent.Layout()

    def __on_choice(self, event):
        _new_app = AppList.get()[self.GetSelection()]
        AppList.set_active_installation(_new_app)
        print(f"Active Install set to: {AppList.get_active_installation()}")


class BBJFrame(wx.Frame):
    __app_picker: AppPicker

    def __init__(self, parent, title, pos, size):
        super(BBJFrame, self).__init__(
            parent=parent, title=title, pos=pos, size=size)
        self.init_frame()
        self.Layout()
        self.Centre()

    def init_frame(self):

        # menu bar stuff
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()

        file_item = file_menu.Append(wx.ID_EXIT, "Quit", "Quit application")

        menu_bar.Append(file_menu, "&File")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.close_application, file_item)

        # content
        # panel = wx.Panel(self)

        # vbox = wx.BoxSizer(wx.VERTICAL)
        # hbox = wx.BoxSizer(wx.HORIZONTAL)

        # app_picker_label = wx.StaticText(
        #     panel, wx.ID_ANY, "Blender Installations: ")
        # hbox.Add(app_picker_label)
        # self.__app_picker = AppPicker(panel)
        # hbox.Add(self.__app_picker)
        # button = wx.Button(panel, label="Add")
        # hbox.Add(button, flag=wx.LEFT, border=10)
        # button.Bind(event=wx.EVT_BUTTON, handler=self.add_blender_installation)

        # vbox.Add(hbox, flag=wx.EXPAND | wx.ALL, border=10)
        # vbox.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.ALL, border=10)

        # panel.SetSizer(vbox)

        vboxsizer_app_main = wx.BoxSizer(wx.VERTICAL)

        hboxsizer_apppicker = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_apppicker = wx.StaticText(
            self, wx.ID_ANY, u"Blender Installations", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_apppicker.Wrap(-1)

        hboxsizer_apppicker.Add(self.lbl_apppicker, 0,
                                wx.ALIGN_CENTER | wx.LEFT, 30)

        self.__app_picker = AppPicker(self)

        hboxsizer_apppicker.Add(
            self.__app_picker, 0, wx.ALIGN_CENTER | wx.LEFT, 20)

        self.btn_add_app = wx.Button(
            self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0)
        self.btn_add_app.SetToolTip(u"Add new blender installation")
        self.btn_add_app.Bind(event=wx.EVT_BUTTON,
                              handler=self.add_blender_installation)

        hboxsizer_apppicker.Add(self.btn_add_app, 0,
                                wx.ALIGN_CENTER | wx.LEFT, 10)

        vboxsizer_app_main.Add(hboxsizer_apppicker, 0, wx.EXPAND | wx.TOP, 10)

        hboxsizer_main_content = wx.BoxSizer(wx.HORIZONTAL)

        self.notebook_main_content = wx.Notebook(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.panel_render_queue = wx.Panel(
            self.notebook_main_content, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        vboxsizer_render_queue = wx.BoxSizer(wx.VERTICAL)

        hboxsizer_render_control = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_add_job = wx.Button(
            self.panel_render_queue, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0)
        hboxsizer_render_control.Add(
            self.btn_add_job, 0, wx.ALIGN_CENTER | wx.LEFT, 20)

        self.btn_save_joblist = wx.Button(
            self.panel_render_queue, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0)
        hboxsizer_render_control.Add(
            self.btn_save_joblist, 0, wx.ALIGN_CENTER | wx.LEFT, 10)

        self.btn_load_joblist = wx.Button(
            self.panel_render_queue, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0)
        hboxsizer_render_control.Add(self.btn_load_joblist, 0, wx.LEFT, 10)

        vboxsizer_render_queue.Add(
            hboxsizer_render_control, 0, wx.EXPAND | wx.TOP, 10)

        hboxsizer_job_list = wx.BoxSizer(wx.HORIZONTAL)

        # render job list table data
        self.m_dataViewListCtrl5 = wx.dataview.DataViewListCtrl(
            self.panel_render_queue, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 | wx.BORDER_NONE)

        self.m_dataViewListColumn1 = self.m_dataViewListCtrl5.AppendTextColumn(
            u"#", wx.dataview.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT, wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.m_dataViewListColumn3 = self.m_dataViewListCtrl5.AppendTextColumn(
            u"Name", wx.dataview.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE)
        self.m_dataViewListColumn4 = self.m_dataViewListCtrl5.AppendTextColumn(
            u"Name", wx.dataview.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE)

        hboxsizer_job_list.Add(self.m_dataViewListCtrl5,
                               1, wx.ALL | wx.EXPAND, 0)

        vboxsizer_render_queue.Add(
            hboxsizer_job_list, 1, wx.EXPAND | wx.TOP, 10)

        self.panel_render_queue.SetSizer(vboxsizer_render_queue)
        self.panel_render_queue.Layout()
        vboxsizer_render_queue.Fit(self.panel_render_queue)
        self.notebook_main_content.AddPage(
            self.panel_render_queue, u"Render Queue", True)
        self.panel_render_log = wx.Panel(
            self.notebook_main_content, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel_render_log.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))

        vboxsizer_log_content = wx.BoxSizer(wx.VERTICAL)

        self.log_txtbox = wx.TextCtrl(self.panel_render_log, wx.ID_ANY, wx.EmptyString,
                                      wx.DefaultPosition, wx.DefaultSize, 0 | wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER | wx.WANTS_CHARS | wx.TE_READONLY | wx.TE_MULTILINE)
        self.log_txtbox.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))

        vboxsizer_log_content.Add(self.log_txtbox, 1, wx.ALL | wx.EXPAND, 20)

        self.panel_render_log.SetSizer(vboxsizer_log_content)
        self.panel_render_log.Layout()
        vboxsizer_log_content.Fit(self.panel_render_log)
        self.notebook_main_content.AddPage(
            self.panel_render_log, u"Log", False)

        hboxsizer_main_content.Add(
            self.notebook_main_content, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)

        vboxsizer_app_main.Add(hboxsizer_main_content,
                               1, wx.EXPAND | wx.TOP, 10)

        hboxsizer_progress = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_progress_bar = wx.StaticText(
            self, wx.ID_ANY, u"Progress", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_progress_bar.Wrap(-1)

        hboxsizer_progress.Add(self.lbl_progress_bar, 0,
                               wx.ALIGN_BOTTOM | wx.LEFT, 30)

        self.progress_bar = wx.Gauge(
            self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
        self.progress_bar.SetValue(25)
        hboxsizer_progress.Add(self.progress_bar, 1, wx.LEFT | wx.RIGHT, 30)

        vboxsizer_app_main.Add(hboxsizer_progress, 0, wx.EXPAND | wx.TOP, 10)

        hboxsizer_renderstart = wx.BoxSizer(wx.HORIZONTAL)

        self.chkbox_shutdown_after = wx.CheckBox(
            self, wx.ID_ANY, u"Shutdown after completion  ", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT)
        hboxsizer_renderstart.Add(
            self.chkbox_shutdown_after, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 25)

        self.btn_start_render = wx.Button(
            self, wx.ID_ANY, u"Render", wx.DefaultPosition, wx.DefaultSize, 0)
        hboxsizer_renderstart.Add(self.btn_start_render, 0, wx.RIGHT, 30)

        vboxsizer_app_main.Add(hboxsizer_renderstart, 0,
                               wx.ALIGN_RIGHT | wx.BOTTOM | wx.TOP, 15)

        self.SetSizer(vboxsizer_app_main)

    def add_blender_installation(self, event) -> bool:
        with wx.FileDialog(self, "Add new blender installation", wildcard="Blender Executeable|blender; blender.exe", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return False

            path = file_dialog.GetPath()

            try:
                if not AppList.add_installation(path):
                    return False

                self.__app_picker.update()
                return True

            except:
                print("Error File Dialog")
                return False

    def close_application(self, event):
        self.Close()
