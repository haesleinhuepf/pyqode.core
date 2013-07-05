#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains utility functions
"""
import glob
import os
import sys
import pcef
from pcef.qt import QtCore, QtGui


def findSettingsDirectory(appName="PCEF"):
    """
    Creates and returns the path to a directory that suits well to store app/lib
    settings on Windows and Linux.
    """
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        pth = os.path.join(home, appName)
    else:
        pth = os.path.join(home, ".%s" % appName)
    if not os.path.exists(pth):
        os.mkdir(pth)
    return pth


class TextStyle(object):
    """
    Defines a text style: a color associated with text style options (bold,
    italic and underline).

    This class has methods to set the text style from a string and to easily
    be created from a string.
    """

    def __init__(self, style=None):
        """
        :param style: The style string ("#rrggbb [bold] [italic] [underlined])
        """
        self.color = QtGui.QColor()
        self.bold = False
        self.italic = False
        self.underlined = False
        if style:
            self.from_string(style)

    def __str__(self):
        color = self.color.name()
        bold = "nbold"
        if self.bold:
            bold = "bold"
        italic = "nitalic"
        if self.italic:
            italic = "italic"
        underlined = "nunderlined"
        if self.underlined:
            underlined = "underlined"
        return " ".join([color, bold, italic, underlined])

    def from_string(self, string):
        tokens = string.split(" ")
        assert len(tokens) == 4
        self.color = QtGui.QColor(tokens[0])
        self.bold = False
        if tokens[1] == "bold":
            self.bold = True
        self.italic = False
        if tokens[2] == "italic":
            self.italic = True
        self.underlined = False
        if tokens[1] == "underlined":
            self.underlined = True


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def find_subpackages(pkgpath):
    import pkgutil
    for itm in pkgutil.iter_modules([pkgpath]):
        print(itm)





class InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

class Invoker(QtCore.QObject):
    def event(self, event):
        event.fn(*event.args, **event.kwargs)
        return True



class JobThread(QtCore.QThread):
    '''Class for implement a thread, can be used and stoppen in any moment.
        * extend and override the run method and if you want onFinish
    '''

    __name = "JobThread({}{}{})"

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.__jobResults = None
        self.args = ()
        self.kwargs = {}

    @staticmethod
    def stopJobThreadInstance(caller, method, *args, **kwargs):
        caller.invoker = Invoker()
        caller.invokeEvent = InvokeEvent(method, *args, **kwargs)
        QtCore.QCoreApplication.postEvent(caller.invoker, caller.invokeEvent)

    def __repr__(self):
        if hasattr(self,"executeOnRun"):
            name = self.executeOnRun.__name__
        else:
            name = hex(id(self))
        return self.__name.format(name,self.args,self.kwargs)

    def stopRun(self):
        self.onFinish()
        self.terminate()

    def setMethods(self, onRun, onFinish):
        self.executeOnRun = onRun
        self.executeOnFinish = onFinish

    def setParameters(self, *a, **kw):
        self.args = a
        self.kwargs = kw

    def onFinish(self):
        if hasattr(self,"executeOnFinish") and self.executeOnFinish and hasattr(self.executeOnFinish, '__call__'):
            self.executeOnFinish()

    def run(self):
        if hasattr(self,"executeOnRun") and self.executeOnRun and hasattr(self.executeOnRun, '__call__'):
            self.executeOnRun( *self.args, **self.kwargs )
            self.onFinish()
        else:
            raise Exception("Executing not callable statement")


class JobRunner:
    '''Class JobRunner, created to do a job and stop at anytime.
    If user Force=True the actual JobRunner is stopped 
    and the new JobRunner is created.'''

    __jobqueue = []
    __jobRunning = False

    def __init__(self, caller):
        self.caller = caller

    def __repr__(self):
        return repr(self.__jobqueue[0] if len(self.__jobqueue)>0 else "None")

    def startJob(self, callable, force, *args, **kwargs):
        '''function startJob, created to start a JobRunner.'''
        thread = JobThread()
        thread.setMethods(callable, self.executeNext)
        thread.setParameters(*args, **kwargs)
        if force:
            self.__jobqueue.append( thread )
            self.stopJob()
        else:
            self.__jobqueue.append( thread )
        if not self.__jobRunning:
            self.__jobqueue[0].setMethods(callable, self.executeNext)
            self.__jobqueue[0].setParameters(*args, **kwargs)
            self.__jobqueue[0].start()
            self.__jobRunning = True

    def executeNext(self):
        self.__jobRunning = False
        if len(self.__jobqueue)>0:
            self.__jobqueue.pop(0)
        if len(self.__jobqueue)>0:
            self.__jobqueue[0].start()
            self.__jobRunning = True            

    def stopJob(self):
        '''function stopJob, created to stop a JobRunner at anytime.'''
        if len(self.__jobqueue)>0:
            JobThread.stopJobThreadInstance(self.caller, self.__jobqueue[0].stopRun)




if __name__ == '__main__':
    import time
    class ventana(QtGui.QWidget):

        def __init__(self):
            QtGui.QWidget.__init__(self,parent=None)
            self.btn = QtGui.QPushButton(self)
            self.btn.setText("Stop Me!!!")
            QtCore.QObject.connect( self.btn, QtCore.SIGNAL( "clicked()" ), self.hola)
            ############################################
            self.hilo = JobRunner(self)
            self.hilo.startJob(self.xxx ,False, 'Stop')
            self.hilo.startJob(self.xxx ,False, 'Repeat')
            ############################################

        def xxx(self, action):
            while 1:
                self.btn.setText(":O")
                time.sleep(1)
                self.btn.setText("{} Me!!!".format(action))
                time.sleep(1)
        def hola(self):
            self.hilo.stopJob()
            self.btn.setText("Thanks!!!")


    import sys
    app = QtGui.QApplication(sys.argv)
    v = ventana()
    v.show()
    sys.exit(app.exec_())

