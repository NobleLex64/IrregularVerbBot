# IrregularVerbBot

Windows:

How install and run:
	
	// >> - is your console input

	>> git clone https://github.com/NobleLex64/IrregularVerbBot.git
	>> cd IrregularVerbBot\
	>> ./start_bot.bat
	>> BOT_TOKEN: 
	>> Here your tg bot token
	>> N/Y	
	>> Y
	>> Y

IF YOU STARTED ./start_bot.bat AT LEAST ONCE, you can just run IrregularVerbBot\src\start.bat
ALSO FOR STOP BOT ENTER >> Ctr+C in cmd where .bat

Linux:

How install and run:
	
	// >> - is your console input

	>> git clone https://github.com/NobleLex64/IrregularVerbBot.git
	>> cd IrregularVerbBot/
	>> chmod +x start_bot.sh
	>> ./start_bot.sh
	>> BOT_TOKEN: 
	>> Here your tg bot token
	>> N/Y	
	>> Y
	>> Y

IF YOU STARTED ./start_bot.sh AT LEAST ONCE, you can just run IrregularVerbBot\src\start.sh
ALSO FOR STOP BOT ENTER >> Ctr+C in cmd where .sh

Background picture:
	if you need other image you can put in folder: IrregularVerbBot\src\data\BackgroundImage\
	the first file in this folder will be installed
	if you don't need background image clear IrregularVerbBot\src\data\BackgroundImage\ folder.	

./src/src/.env - configurate file you can modificate this param

	VERB_ON_PAGE=15 // How many verbs on 1 page in irregular verb table

	VERB_TEXT_COLOR=0xDC140C //  Color irregular verbs
	VERB_TRANSLATION_COLOR=0x228B22 // Color translation verb
	FONT=arial.ttf // font

	// Size and background color for irregular verb carts
	CARTS_WIDTH=800 
	CARTS_HEIGHT=450
	CARTS_BACKGROUND_COLOR=0xFFFFFFE0
	CARTS_TEXT_SIZE=40

	// Size and background color for irregular verb table
	TABLE_WIDTH=1600
	TABLE_HEIGHT=900
	TABLE_BACKGROUND_COLOR=0xFFFFFF00
	TABLE_HEADER_TEXT_COLOR=0x4040FF
	TABLE_HEADER_TEXT_SIZE=30
	TABLE_TEXT_SIZE=25