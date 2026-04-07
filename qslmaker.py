import adif_io as aio
from PIL import Image, ImageDraw, ImageFont
import os

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '', value).strip().lower())
    value = str(re.sub('[-\s]+', '-', value))
    return value

def drawCenteredText(text, textarea, font_in, font_color='rgb(0,0,0)'):
    #returns a two-tuple (x,y) location for text.
    #note: ONLY CENTERS HORIZONTALLY at this time
    bbox = draw.textbbox((0, 0), text, font=font_in)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = ((textarea['size'][0] - w)/2) + textarea['offset'][0]
    y = ((textarea['size'][1] - h)/2) + textarea['offset'][1]
    draw.text((x,y), text, font=font_in, fill=font_color)

fontfile = 'fonts/RobotoCondensed-Regular.ttf'
font = ImageFont.truetype(fontfile, size=73)
boldfontfile = 'fonts/RobotoCondensed-Bold.ttf'
call_font = ImageFont.truetype(boldfontfile, size=93)
bold_font = ImageFont.truetype(boldfontfile, size=73)
bolditalicfontfile = 'fonts/RobotoCondensed-BoldItalic.ttf'
bolditalic_font = ImageFont.truetype(boldfontfile, size=73)
rst_font = ImageFont.truetype(fontfile, size=49)
sig_font = ImageFont.truetype(bolditalicfontfile, size=73)

imageinfo = [ {
    'filename': 'cards/test_qsl-0407.jpg',
    'fields': {
        'to_radio': {'offset': (984.2, 140.6), 'size': (610.9, 100)},
        'date': {'offset': (70.5, 354.3), 'size': (389.8, 100)},
        'cst_time': {'offset': (495.7, 354.3), 'size': (236.2, 125)},
        'time': {'offset': (767.1, 354.3), 'size': (236.2, 100)},
        'freq': {'offset': (1037.7, 354.3), 'size': (236.2, 100)},
        'mode': {'offset': (1310, 354.3), 'size': (272.7, 100)},
        'rst': {'offset': (1040.3, 519.7), 'size': (236.2, 100)},
        'rig_ant': {'offset': (70.9, 519.7), 'size': (661.7, 100)},
        'pwr': {'offset': (768.2, 519.7), 'size': (236.2, 100)},
        'cfm_qso': {'offset': (1377.2, 263.4), 'size': (219, 9)},
        'cfm_rpt': {'offset': (1198.2, 263.4), 'size': (171, 9)},
        'pse_qsl': {'offset': (1337.5, 575.6), 'size': (219, 9)},
        'tnx_qsl': {'offset': (1337.5, 520), 'size': (219, 9)},
        'rmks': {'offset': (70.9, 685), 'size': (1511.8, 271.7)},
        'op': {'offset': (1199, 986), 'size': (381, 158)},
        } }
    ]

card_no = 0
qso_flag = True
# qso_flag = False
pse_flag = True
# pse_flag = False
adif_file = 'tony.adi'
sig_img = Image.open('cards/tony_sign.png')

fields = imageinfo[card_no]['fields']
adif = aio.read_from_file(adif_file)

ratio =  sig_img.height / fields['op']['size'][1]
(im_w, im_h) = (int(sig_img.width // ratio), int(sig_img.height // ratio))
sig_img_r = sig_img.resize((im_w, im_h))

black = 'rgb(0,0,0)'
red = 'rgb(255,0,0)'
darkred = 'rgb(201,29,29)'
blue= 'rgb(0,0,255)'

for qso in adif[0]:
    print(f"Working on {qso['CALL']}")
    image = Image.open(imageinfo[card_no]['filename'])
    draw = ImageDraw.Draw(image)
    # CALL
    drawCenteredText(qso['CALL'], fields['to_radio'], call_font, black)
    #QSO DATE
    day = qso['QSO_DATE'][-2:]
    month = qso['QSO_DATE'][4:6]
    year = qso['QSO_DATE'][0:4]
    date = "{}-{}-{}".format(year, month, day)
    drawCenteredText(date, fields['date'], bold_font, black)
    #QSO Time ON
    hours = int(qso['TIME_ON'][:2])
    minutes = int(qso['TIME_ON'][2:4])
    cst_hours = (hours + 8) % 24
    cst_date_flag = True if hours + 8 > 23 \
        else False
    time = f"{hours:02d}:{minutes:02d}"
    cst_time = f"(+0){cst_hours:02d}:{minutes:02d}" if not cst_date_flag \
        else f"(+1){cst_hours:02d}:{minutes:02d}"
    drawCenteredText(cst_time, fields['cst_time'], bold_font, black)
    drawCenteredText(time, fields['time'], bold_font, black)

    #QSO Frequency
    freq = qso['FREQ'][:7]
    drawCenteredText(freq, fields['freq'], bold_font, darkred)

    #QSO mode
    qso_mode = qso['MODE']
    drawCenteredText(qso_mode, fields['mode'], bold_font, black)

    #RST
    rst = qso['RST_SENT']
    drawCenteredText(rst, fields['rst'], bold_font, black)

    #RIG & ANT & PWR
    rig_ant = '{}, {}'.format(qso['MY_RIG'], qso['MY_ANTENNA'])
    drawCenteredText(rig_ant, fields['rig_ant'], bold_font, black)
    pwr = qso['TX_PWR']
    drawCenteredText(pwr, fields['pwr'], bold_font, darkred)

    #Confirming QSO or UR RPT
    drawCenteredText('-------', fields['cfm_qso'] if qso_flag else fields['cfm_rpt'], bold_font, darkred)
    #PSE/PLS or TNX QSL
    #draw.text(imageinfo['pse_qsl'], 'x', fill=red, font=bold_font)
    drawCenteredText('-------', fields['pse_qsl'] if pse_flag else fields['tnx_qsl'], bold_font, darkred)

    #rmks
    # drawCenteredText('de Scott N8VSI', fields['73'], sig_font, blue)
    #op
    # image.paste(sig_img_r, fields['op']['offset'], mask = sig_img_r)

    filecall = slugify(qso['CALL'])
    filedatetime = str(qso['QSO_DATE'][:4])+str(month)+str(day) + '_' + str(qso['TIME_ON'])
    if not os.path.exists('out'):
        os.makedirs('out')
    image.save(f"out/{filecall}_{filedatetime}.jpg")
