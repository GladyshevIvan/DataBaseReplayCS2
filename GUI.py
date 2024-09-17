import wx
from ConvertStatsToStream import ActionWithData


class MyFrame(wx.Frame):
    def __init__(self, parent, title, style, size=(400, 280)):
        super().__init__(parent, title=title, style=style, size=size)

        panel = wx.Panel(self)
        fb = wx.FlexGridSizer(4, 2, 10, 10)
        vertical_box_sizer = wx.BoxSizer(wx.VERTICAL)

        self.path_text = wx.TextCtrl(panel)
        self.date_text = wx.TextCtrl(panel)
        self.batabase_action = wx.RadioBox(panel, label="Выберите вариант", choices=['Ничего не делать', 'Записать матч', 'Извлечь матч'], majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.to_stream = wx.CheckBox(panel)

        fb.AddMany([
            (wx.StaticText(panel, label='Путь к файлу или название')),
            (self.path_text, wx.ID_ANY, wx.EXPAND),
            (wx.StaticText(panel, label='Дата и время')),
            (self.date_text, wx.ID_ANY, wx.EXPAND),
            (wx.StaticText(panel, label='Действие с Базой Данных')),
            (self.batabase_action),
            (wx.StaticText(panel, label='В эфир')),
            (self.to_stream)
        ])

        fb.AddGrowableCol(1, 1)
        vertical_box_sizer.Add(fb, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Кнопки
        button_enter = wx.Button(panel, id=0, label='Ввод')
        button_stop = wx.Button(panel, id=1, label='Отмена')

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(button_enter, 0, wx.LEFT, 10)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(button_stop, 0, wx.RIGHT, 10)
        vertical_box_sizer.Add(button_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        panel.SetSizer(vertical_box_sizer)

        self.Bind(wx.EVT_BUTTON, self.RunScript, id=0)
        self.Bind(wx.EVT_BUTTON, self.StopScript, id=1)


    def RunScript(self, event):
        raw_dem = self.path_text.GetValue()
        date_and_time = self.date_text.GetValue()
        database_action_choice = self.batabase_action.GetStringSelection()
        to_stream_choice = self.to_stream.GetValue()

        if not raw_dem:
            raise Exception()

        ActionWithData(raw_dem, date_and_time, database_action_choice, to_stream_choice)

    def StopScript(self, event):
        print(1)

app = wx.App()

frame = MyFrame(None, title='CS2 DataBase', style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX & ~wx.RESIZE_BORDER)
frame.Center()
frame.Show()

app.MainLoop()