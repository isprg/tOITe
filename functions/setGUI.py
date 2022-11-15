import PySimpleGUI as sg


# GUI設定 =============================================================
def setGUI(dictLayout):
	sDisplayWidth = 1024
	sDisplayHeight = 600

	sg.set_options(font=("", 13), margins=(0, 0))
	sg.theme("BrownBlue")

	dictWindow = {}
	for name, layout in dictLayout.items():
		if layout == "None":
			dictWindow[name] = "None"
		else:
			dictWindow[name] = sg.Window(
				name,
				layout,
				size=(sDisplayWidth, sDisplayHeight),
				location=(0, 0),
				#no_titlebar=False,
				no_titlebar=True,
				finalize=True,
			)

	return dictWindow
