import PySimpleGUI as sg

sDisplayWidth = 1024
sDisplayHeight = 600

def MakeMainWindow():
	sg.set_options(font=("", 12), margins=(0, 0))
	sg.theme("DarkBlue17")

	Button_Size = (15, 3)

	left_space = 0
	top_space = 20
	layout = [
		[
			sg.Column(
				[[sg.Button("プログラム終了", key="end", size=Button_Size,)]],
				justification="c",
				pad=((left_space, 0), (top_space, 0)),
			)
		],
		[
			sg.Column(
				[[sg.Button("ゲームリセット", key="reset", size=Button_Size)]],
				justification="c",
				pad=((left_space, 0), (top_space, 0)),
			)
		],
		[
			sg.Column(
				[[sg.Button("管理者カードの登録", key="register", size=Button_Size)]],
				justification="c",
				pad=((left_space, 0), (top_space, 0)),
			)
		],
		[
			sg.Column(
				[[sg.Button("カードの記録を編集", key="edit", size=Button_Size)]],
				justification="c",
				pad=((left_space, 0), (top_space, 0)),
			)
		],
	]


	# メインウィンドウ
	window = sg.Window(
		"MainWindow",
		layout,
		size=(sDisplayWidth, sDisplayHeight),
		location=(0, 0),
		no_titlebar=True,
		finalize=True,
	)

	return window


def MakeEditWindow(dictFlag):
	layoutSetCard = [
		[
			sg.Column(
				[[sg.Text("編集したいカードを設置した状態で「編集ボタン」を押してください．")]],
				pad=((0, 0), (200, 0)),
			)
		],
		[
			sg.Button("編集", key="edit"),
			sg.Button("終了", key="end"),
		],
	]
	
	listFlagKeys = list(dictFlag.keys())
	listFlagValues = list(dictFlag.values())

	layoutEdit = [
		[
			sg.Column(
				[
					[
						sg.Text(
							"チェックを追加するとクリア済みになります．\n編集が完了したら書き込みボタンを押してください．",
							font=("", 18),
						)
					]
				],
				pad=((0, 0), (50, 0)),
				justification="c",
			)
		],
		[
			sg.Frame(
				"ゲーム一覧",
				[
					[sg.Checkbox(listFlagValues[0], key=listFlagKeys[0])],
					[sg.Checkbox(listFlagValues[1], key=listFlagKeys[1])],
					[sg.Checkbox(listFlagValues[2], key=listFlagKeys[2])],
					[sg.Checkbox(listFlagValues[3], key=listFlagKeys[3])],
				],
				pad=((300, 0), (0, 0)),
			)
		],
		[
			sg.Column(
				[
					[
						sg.Button("書き込み", key="write"),
						sg.Button("戻る", key="return"),
					],
				],
				justification="c",
			)
		],
	]

	winSetCard = sg.Window(
		"SetCard_Window",
		layoutSetCard,
		size=(sDisplayWidth, sDisplayHeight),
		location=(0, 0),
		element_justification="center",
		finalize=True,
		no_titlebar=True,
	)

	winEdit = sg.Window(
		"Edit_Window",
		layoutEdit,
		size=(sDisplayWidth, sDisplayHeight),
		location=(0, 0),
		finalize=True,
		no_titlebar=True,
	)

	return winSetCard, winEdit


def MakeRegisterAdminWindow(strText):
	layout = [
		[sg.Multiline(default_text=strText, key="ID_list", expand_x=True, expand_y=True)],
		[sg.Text("管理者カードを新規登録するには，カードを設置した状態で「登録ボタン」を押してください．", font=("", 15))],
		[sg.Text("管理者カードの登録を削除するには，上のテキストボックスから直接IDを削除してください．", font=("", 15))],
		[sg.Button("登録", key="register"), sg.Button("終了", key="end")],
	]
	
	window = sg.Window(
		"RegisterWindow",
		layout,
		size=(sDisplayWidth, sDisplayHeight),
		location=(0, 0),
		finalize=True,
		no_titlebar=True,
	)

	return window
