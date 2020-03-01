# Cura plug-in to read SVG files as toolpaths.
# Copyright (C) 2020 Ghostkeeper
# This plug-in is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this plug-in. If not, see <https://gnu.org/licenses/>.

import os.path  # To find the QML file to display.
import PyQt5.QtCore  # To display an interface to the user.
import threading  # To wait for the user to close the UI.
import UM.Application
import UM.Mesh.MeshReader  # To return the correct prompt response for the preread.

class Configuration(PyQt5.QtCore.QObject):
	"""
	This class shows a dialogue that asks the user how he'd like to load the
	file.

	You can show the dialogue with the ``prompt`` function.
	"""

	_show_ui_trigger = PyQt5.QtCore.pyqtSignal()
	"""
	Signal to show the UI.

	This is necessary because the UI can only be created on the QML Engine
	thread. Creating it from the emittance of this trigger moves the creation
	to that thread.
	"""

	def __init__(self) -> None:
		"""
		Creates the configuration object.

		This doesn't create the actual UI yet. That will be created lazily by
		the ``prompt`` function.
		"""
		super().__init__(parent=UM.Application.Application.getInstance())
		self.ui_element = None
		self._file_name = None
		self._ui_lock = threading.Lock()
		self._status = UM.Mesh.MeshReader.MeshReader.PreReadResult.failed
		self._show_ui_trigger.connect(self._prompt)

	def prompt(self, file_name) -> UM.Mesh.MeshReader.MeshReader.PreReadResult:
		"""
		Asks the user how he'd like to read the file.

		This will show a dialogue to the user with some options. The thread
		will be blocked until the dialogue is closed.
		:param file_name: The path to the file that is to be read.
		:return: The result of the dialogue, whether it is accepted, declined
		or there was an error.
		"""
		self._file_name = file_name
		self._show_ui_trigger.emit()
		self._wait_for_ui()
		return self._status

	def create_ui(self):
		"""
		Loads the dialogue element from the QML file.
		"""
		application = UM.Application.Application.getInstance()
		qml_path = os.path.join(application.getPluginRegistry().getPluginPath("SVGToolpathReader"), "ConfigurationDialogue.qml")
		self.ui_element = application.createQmlComponent(qml_path, {"manager": self})
		self.ui_element.setFlags(self.ui_element.flags() & ~PyQt5.QtCore.Qt.WindowCloseButtonHint & ~PyQt5.QtCore.Qt.WindowMinimizeButtonHint & ~PyQt5.QtCore.Qt.WindowMaximizeButtonHint)
		self.ui_element.show()

	def _prompt(self) -> UM.Mesh.MeshReader.MeshReader.PreReadResult:
		"""
		Actually asks the user how he'd like to read the file.

		This time it will be executed in the QML engine thread so that new
		elements can be created if necessary.
		:param file_name: The path to the file that is to be read.
		:return: The result of the dialogue, whether it is accepted, declined
		or there was an error.
		"""
		print("Test prompt!", self._file_name)
		if self.ui_element is None:
			self.create_ui()
		self._ui_lock.acquire()
		return UM.Mesh.MeshReader.MeshReader.PreReadResult.accepted

	def _wait_for_ui(self):
		self._ui_lock.acquire()
		self._ui_lock.release()