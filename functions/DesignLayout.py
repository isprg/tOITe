import PySimpleGUI as sg


def make_4choice_layout(
	strImage_path, listBottom_text, listBottom_disabled=[False, False, False, False]
):
	top_space = 23
	left_space = 25

	Button_Size = (8, 3)
	layout = [
		[
			sg.Image(strImage_path, pad=((0, 0), (0, 0)), enable_events=True),
			sg.Column(
				[
					[
						sg.Column(
							[
								[
									sg.Button(
										listBottom_text[0],
										size=Button_Size,
										pad=((0, 0), (0, 0)),
										disabled=listBottom_disabled[0],
									)
								]
							],
							pad=((left_space, 0), (top_space, 0)),
						)
					],
					[
						sg.Column(
							[
								[
									sg.Button(
										listBottom_text[1],
										size=Button_Size,
										pad=((0, 0), (0, 0)),
										disabled=listBottom_disabled[1],
									)
								]
							],
							pad=((left_space, 0), (top_space, 0)),
						)
					],
					[
						sg.Column(
							[
								[
									sg.Button(
										listBottom_text[2],
										size=Button_Size,
										pad=((0, 0), (0, 0)),
										disabled=listBottom_disabled[2],
									)
								]
							],
							pad=((left_space, 0), (top_space, 0)),
						)
					],
					[
						sg.Column(
							[
								[
									sg.Button(
										listBottom_text[3],
										size=Button_Size,
										pad=((0, 0), (0, 0)),
										disabled=listBottom_disabled[3],
									)
								]
							],
							pad=((left_space, 0), (top_space, 0)),
						)
					],
				],
				size=(288, 600),
				pad=((0, 0), (0, 0)),
			),
		],
	]

	return layout


def make_fullimage_layout(strImagePath, strKey):
	layout = [
		[
			sg.Image(strImagePath, pad=((0, 0), (0, 0)), enable_events=True, key=strKey),
		],
	]

	return layout
