import wx
class PathBrowser(wx.TreeCtrl):
    def __init__(self, parent, remote_root):
        wx.TreeCtrl.__init__(self, parent, size=(-1,200))
        self.jobs = wx.GetApp().daemon.jobs
        self.remote_root = remote_root
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_expand)
        self.load_root()

    def on_expand(self, evt):
        node = evt.GetItem()
        if not self.GetPyData(node)['loaded']:
            self.load_children(node)
        evt.Skip()

    def load_root(self):
        self.root_node = self.AddRoot('Root')
        self.SetPyData(self.root_node, {'path': self.remote_root, 'loaded': False})
        self.load_children(self.root_node)

    def load_children(self, node):
        self.SetItemText(node, self.GetItemText(node) + ' [loading...]')
        command = 'execute_capture'
        args = ['find', self.GetPyData(node)['path'], '-maxdepth','1','-type','d','-readable']
        self.jobs.appendleft((command, args, self.make_callback(node)))

    def make_callback(self, node):
        def callback(output):
            data = self.GetPyData(node)
            data['loaded'] = True
            self.SetItemText(node, self.GetItemText(node).replace(' [loading...]',''))
            self.SetPyData(node, data)
            for dir in output.split('\n')[1:-1]:
                child = self.AppendItem(node, dir.replace(data['path'],'').replace('/',''))
                self.SetItemHasChildren(child, True)
                self.SetPyData(child, {'path': dir, 'loaded': False})
            self.Expand(node)
        return callback

