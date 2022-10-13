
from multiprocessing.pool import ApplyResult
import wx
import wx.dataview
import wx.grid

from appmanager import AppList, AppSettings
from rendermanager import JobList, JobStatus


class BBJGUI(wx.App):

    class BBJFrame(wx.Frame):

        class BBJButton(wx.Button):
            def __init__(self, parent, label, disabled_label, tooltip, disabled_tooltip):
                super().__init__(parent, wx.ID_ANY, label, wx.DefaultPosition, wx.DefaultSize, 0)
                self.label = label
                self.disabled_label = disabled_label
                self.tooltip = tooltip
                self.disabled_tooltip = disabled_tooltip
                self.update()

            def update(self, validator: bool = False):
                if validator:
                    self.SetToolTip(self.tooltip)
                    self.SetLabel(self.label)
                    self.Enable()
                else:
                    self.SetToolTip(self.disabled_tooltip)
                    self.SetLabel(self.disabled_label)
                    self.Disable()

        class AppPicker(wx.Choice):
            def __init__(self, parent):
                super().__init__(parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
                self.Bind(wx.EVT_CHOICE, self.__on_choice)
                self.update()

            def update(self):
                self.Clear()
                self.SetToolTip("Add at least one valid Blender installation")
                if AppList.is_populated():
                    self.Append(AppList.get_choice_list())
                    self.SetSelection(AppList.get_active_installation_index())
                    self.SetToolTip("Pick default Blender installation")
                self.SetSize(self.GetBestSize())
                _parent: BBJGUI.BBJFrame = self.Parent
                _parent.Layout()

            def __on_choice(self, event):
                _new_app = AppList.get()[self.GetSelection()]
                AppList.set_active_installation(_new_app)
                print(f"Active Install set to: {AppList.get_active_installation()}")

        class JobTableView(wx.grid.Grid):

            class TableBase(wx.grid.GridTableBase):

                def __init__(self) -> None:
                    super().__init__()
                    self.col_labels = ["ID", "Blend File", "Status"]
                    self.data_types = [wx.grid.GRID_VALUE_NUMBER,
                                       wx.grid.GRID_VALUE_STRING,
                                       wx.grid.GRID_VALUE_CHOICE + ":"+JobStatus.get_status_list()
                                       ]
                    self.data = [[0, "", "Queued"]]

                def GetNumberRows(self):
                    return len(self.data) + 1

                def GetNumberCols(self):
                    return len(self.data[0])

                def IsEmptyCell(self, row, col):
                    try:
                        return not self.data[row][col]
                    except IndexError:
                        return True

                def GetValue(self, row, col):
                    try:
                        return self.data[row][col]
                    except IndexError:
                        return ''

                def SetValue(self, row, col, value):
                    def innerSetValue(row, col, value):
                        try:
                            self.data[row][col] = value
                        except IndexError:
                            # add a new row
                            self.data.append([''] * self.GetNumberCols())
                            innerSetValue(row, col, value)

                            # # tell the grid we've added a row
                            # msg = wx.grid.GridTableMessage(self,
                            #                                wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                            #                                1
                            #                                )

                            # self.GetView().ProcessTableMessage(msg)
                    innerSetValue(row, col, value)

                def GetColLabelValue(self, col):
                    return self.col_labels[col]

                def GetTypeName(self, row, col):
                    return self.data_types[col]

                def CanGetValueAs(self, row, col, typeName):
                    _col_type = self.data_types[col].split(":")[0]
                    if typeName == _col_type:
                        return True
                    else:
                        return False

                def CanSetValueAs(self, row, col, typeName):
                    return self.CanGetValueAs(row, col, typeName)

            def __init__(self, parent):
                super().__init__(parent)

                self.table = self.TableBase()
                self.SetTable(self.table, True)
                self.SetRowLabelSize(0)
                self.SetMargins(0, 0)
                self.EnableGridLines(False)
                self.EnableEditing(True)
                self.EnableDragColSize(True)
                self.EnableDragColMove(False)
                # self.AutoSizeColumn(False)

                self.update()

            def update(self):
                self.Layout()

            def add(self, values):
                self.table.data.append(values)

        __app_picker: AppPicker
        __btn_remove_app: BBJButton
        __btn_add_job: BBJButton
        __btn_save_joblist: BBJButton
        __btn_load_joblist: BBJButton
        __btn_start_render: BBJButton
        __job_list: JobTableView

        def __init__(self, parent, title, pos, size):
            super().__init__(parent=parent, title=title, pos=pos, size=size)
            self.init_frame()
            self.Layout()
            self.Centre()

        def init_frame(self):

            # menu bar stuff
            menu_bar = wx.MenuBar()

            mn_file = wx.Menu()

            mi_close = mn_file.Append(wx.ID_EXIT, "Quit", "Quit application")

            menu_bar.Append(mn_file, "&File")

            self.SetMenuBar(menu_bar)

            self.Bind(wx.EVT_MENU, self.close_application, mi_close)

            # content
            vboxsizer_app_main = wx.BoxSizer(wx.VERTICAL)

            # top control section of the app
            hboxsizer_apppicker = wx.BoxSizer(wx.HORIZONTAL)

            self.lbl_apppicker = wx.StaticText(self, label=u"Blender Installations")
            self.lbl_apppicker.Wrap(-1)

            # TODO: setting the size based on Font size
            self.__btn_remove_app = self.BBJButton(self, "x", "x",
                                                   "Remove the currently selected app installation",
                                                   "Add at least one valid Blender installation")
            self.__btn_remove_app.SetMaxSize((30, 30))
            self.__btn_remove_app.Bind(event=wx.EVT_BUTTON, handler=self.remove_blender_installation)

            self.__app_picker = self.AppPicker(self)

            self.btn_add_app = wx.Button(self, label=u"Add")
            self.btn_add_app.SetToolTip(u"Add new blender installation")
            self.btn_add_app.Bind(event=wx.EVT_BUTTON, handler=self.add_blender_installation)

            hboxsizer_apppicker.Add(self.lbl_apppicker, 0, wx.ALIGN_CENTER | wx.LEFT, 30)
            hboxsizer_apppicker.Add(self.__btn_remove_app, 0, wx.ALIGN_CENTER | wx.LEFT, 10)
            hboxsizer_apppicker.Add(self.__app_picker, 0, wx.ALIGN_CENTER | wx.LEFT, 0)
            hboxsizer_apppicker.Add(self.btn_add_app, 0, wx.ALIGN_CENTER | wx.LEFT, 10)

            # render queue and render log section
            hboxsizer_main_content = wx.BoxSizer(wx.HORIZONTAL)

            self.notebook_main_content = wx.Notebook(self)
            self.panel_render_queue = wx.Panel(self.notebook_main_content)

            # render queue page
            vboxsizer_render_queue = wx.BoxSizer(wx.VERTICAL)
            # job list control section
            hboxsizer_render_control = wx.BoxSizer(wx.HORIZONTAL)

            self.__btn_add_job = self.BBJButton(self.panel_render_queue, "Add", u"\u26A0 Add",
                                                "Add .blend file to render queue",
                                                "Add at least one valid Blender installation")
            self.__btn_add_job.Bind(event=wx.EVT_BUTTON, handler=self.add_render_job)

            self.__btn_save_joblist = self.BBJButton(self.panel_render_queue, "Save", "Save",
                                                     "Save the current render queue",
                                                     "Add at least one valid .blend file to the queue")
            self.__btn_save_joblist.Bind(event=wx.EVT_BUTTON, handler=self.save_joblist)

            self.__btn_load_joblist = self.BBJButton(self.panel_render_queue, "Load", u"\u26A0 Load",
                                                     "Load a saved render queue",
                                                     "Add at least one valid Blender installation")
            self.__btn_save_joblist.Bind(event=wx.EVT_BUTTON, handler=self.load_joblist)

            hboxsizer_render_control.Add(self.__btn_add_job, 0, wx.ALIGN_CENTER | wx.LEFT, 20)
            hboxsizer_render_control.Add(self.__btn_save_joblist, 0, wx.ALIGN_CENTER | wx.LEFT, 10)
            hboxsizer_render_control.Add(self.__btn_load_joblist, 0, wx.LEFT, 10)

            # job list section
            hboxsizer_job_list = wx.BoxSizer(wx.HORIZONTAL)

            # TODO: add tabulated data for jobs

            self.__job_list = self.JobTableView(self.panel_render_queue)
            hboxsizer_job_list.Add(self.__job_list, 1, wx.ALL | wx.EXPAND, 0)

            vboxsizer_render_queue.Add(hboxsizer_render_control, 0, wx.EXPAND | wx.TOP, 10)
            vboxsizer_render_queue.Add(hboxsizer_job_list, 1, wx.EXPAND | wx.TOP, 10)

            self.panel_render_queue.SetSizer(vboxsizer_render_queue)
            self.panel_render_queue.Layout()

            vboxsizer_render_queue.Fit(self.panel_render_queue)

            self.notebook_main_content.AddPage(self.panel_render_queue, u"Render Queue", True)

            # render log page
            self.panel_render_log = wx.Panel(self.notebook_main_content)
            self.panel_render_log.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))

            vboxsizer_log_content = wx.BoxSizer(wx.VERTICAL)

            self.log_txtbox = wx.TextCtrl(self.panel_render_log, wx.ID_ANY, wx.EmptyString,
                                          wx.DefaultPosition,
                                          wx.DefaultSize,
                                          0 | wx.VSCROLL | wx.NO_BORDER | wx.WANTS_CHARS | wx.TE_READONLY | wx.TE_MULTILINE)
            self.log_txtbox.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))

            vboxsizer_log_content.Add(self.log_txtbox, 1, wx.ALL | wx.EXPAND, 20)

            self.panel_render_log.SetSizer(vboxsizer_log_content)
            self.panel_render_log.Layout()

            vboxsizer_log_content.Fit(self.panel_render_log)

            self.notebook_main_content.AddPage(self.panel_render_log, u"Log", False)

            hboxsizer_main_content.Add(self.notebook_main_content, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)

            # render progress section
            hboxsizer_progress = wx.BoxSizer(wx.HORIZONTAL)

            self.lbl_progress_bar = wx.StaticText(self, label=u"Progress")
            self.lbl_progress_bar.Wrap(-1)

            self.progress_bar = wx.Gauge(self)
            self.progress_bar.SetValue(25)

            hboxsizer_progress.Add(self.lbl_progress_bar, 0, wx.ALIGN_BOTTOM | wx.LEFT, 30)
            hboxsizer_progress.Add(self.progress_bar, 1, wx.LEFT | wx.RIGHT, 30)

            # render control section
            hboxsizer_renderstart = wx.BoxSizer(wx.HORIZONTAL)

            self.chkbox_shutdown_after = wx.CheckBox(self, label=u"Shutdown after completion  ",
                                                     style=wx.ALIGN_RIGHT)

            _renderbtn_disabled_tooltip = ("Add at least one valid Blender installation and at"
                                           " least one file to the render queue")
            self.__btn_start_render = self.BBJButton(self, "Render", u"\u26A0 Render",
                                                     "Start render process",
                                                     _renderbtn_disabled_tooltip)
            self.__btn_start_render.Bind(event=wx.EVT_BUTTON, handler=self.save_joblist)

            hboxsizer_renderstart.Add(self.chkbox_shutdown_after, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 25)
            hboxsizer_renderstart.Add(self.__btn_start_render, 0, wx.RIGHT, 30)

            # add all app sections to the main vertical sizer
            vboxsizer_app_main.Add(hboxsizer_apppicker, 0, wx.EXPAND | wx.TOP, 10)
            vboxsizer_app_main.Add(hboxsizer_main_content, 1, wx.EXPAND | wx.TOP, 10)
            vboxsizer_app_main.Add(hboxsizer_progress, 0, wx.EXPAND | wx.TOP, 10)
            vboxsizer_app_main.Add(hboxsizer_renderstart, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.TOP, 15)

            self.SetSizer(vboxsizer_app_main)

        def add_blender_installation(self, event) -> bool:
            with wx.FileDialog(self, "Add new blender installation...",
                               wildcard="Blender Executeable|blender; blender.exe",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:

                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    return False

                path = file_dialog.GetPath()

                try:
                    _result = AppList.add_installation(path)
                    self.update_UI()
                    return _result

                except:
                    print("Error File Dialog: Add Blender Installation")
                    return False

        def remove_blender_installation(self, event) -> bool:
            _active_app_index = self.__app_picker.GetSelection()
            _result = AppList.remove_installation(_active_app_index)
            self.update_UI()
            return _result

        def add_render_job(self, event) -> bool:
            with wx.FileDialog(self, "Add .blend file to render queue...",
                               wildcard="Blend File (*.blend)|*.blend",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:

                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    return False

                path = file_dialog.GetPath()

                try:
                    _job = JobList.add_render_job(path)
                    if _job:
                        self.__job_list.add(1, _job.blendfile.path, _job.status)
                        self.update_UI()
                        return True

                    return False

                except:
                    print("Error File Dialog: Add Render Job")
                    return False

        def save_joblist(self, event) -> bool:
            pass

        def load_joblist(self, event) -> bool:
            pass

        def start_render(self, event):
            JobList.render()

        def close_application(self, event):
            self.Close()

        def update_UI(self):
            self.__app_picker.update()
            self.__btn_remove_app.update(AppList.is_populated())
            self.__btn_add_job.update(AppList.is_populated())
            self.__btn_load_joblist.update(AppList.is_populated())
            self.__btn_start_render.update((AppList.is_populated() and JobList.is_populated()))
            # self.__job_list.update()
            self.panel_render_queue.Layout()

    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)

    def OnInit(self):
        _app_name = "Blender Batch Jobs"
        _app_settings = AppSettings(False, "", 1)
        _window_pos = _app_settings.window_position
        _window_size = _app_settings.window_size
        frame = self.BBJFrame(parent=None, title=_app_name, pos=_window_pos, size=_window_size)
        frame.SetMinSize((640, 480))
        frame.Show()
        return True

    def OnExit(self):
        # save stuff
        print("Quitting app")
        return super().OnExit()
