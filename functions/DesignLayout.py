import PySimpleGUI as sg


def makeButton4choice(strButtonText):
	tplSizeOfButton = (8, 3)
	return sg.Button(
		strButtonText,
		size=tplSizeOfButton,
		pad=((0, 0), (0, 0)),
		disabled=False,		
	)


def make_4choice_layout(strImage_path, listButtonText):
	sSpaceTop = 23
	sSpaceLeft = 25

	layout = [[
		sg.Image(strImage_path, pad=((0, 0), (0, 0)), enable_events=True),
		sg.Column(
			[
				[sg.Column(
					[[makeButton4choice(listButtonText[0])]],
					pad=((sSpaceLeft, 0), (sSpaceTop, 0)),
				)],
				[sg.Column(
					[[makeButton4choice(listButtonText[1])]],
					pad=((sSpaceLeft, 0), (sSpaceTop, 0)),
				)],
				[sg.Column(
					[[makeButton4choice(listButtonText[2])]],
					pad=((sSpaceLeft, 0), (sSpaceTop, 0)),
				)],
				[sg.Column(
					[[makeButton4choice(listButtonText[3])]],
					pad=((sSpaceLeft, 0), (sSpaceTop, 0)),
				)],
			],
			size=(224, 600),
			pad=((0, 0), (0, 0)),
		),
	]]

	return layout


def make_fullimage_layout(strImagePath, strKey):
	layout = [[
		sg.Image(strImagePath, pad=((0, 0), (0, 0)), enable_events=True, key=strKey),
	]]

	return layout
