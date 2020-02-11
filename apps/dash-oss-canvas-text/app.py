from PIL import Image
import base64
from io import BytesIO

import dash
import numpy as np
import dash_html_components as html
import dash_core_components as dcc
from dash_canvas import DashCanvas
from dash_canvas.utils import array_to_data_url, parse_jsonstring
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pytesseract

app = dash.Dash(__name__)
server = app.server

canvas_width = 600
canvas_height = 200

app.layout = html.Div([
    # Banner
    html.Div(
        [
            html.Img(src=app.get_asset_url("ocr-logo.png"), className="app__logo"),
            html.H4("Dash OCR", className="header__text"),
        ],
        className="app__header",
    ),
    # Canvas
    html.Div(
        [
            html.Div(
                [
                    html.P('Write inside the canvas with your pencil and press Sign', className='section_title'),
                    html.Div(
                        DashCanvas(id='canvas',
                                   lineWidth=5,
                                   width=canvas_width,
                                   height=canvas_height,
                                   hide_buttons=["zoom", "pan", "line", "pencil", "rectangle", "select"],
                                   lineColor='black',
                                   goButtonTitle='Sign'
                                   )
                        , className="canvas-outer")],
                className='v-card-content'
            ),
            # Annotation Geometry
            html.Div(
                [
                    html.P("Handwriting annotation geometry", className='section_title'),
                    html.Img(id='my-image',
                             width=canvas_width,
                             )
                ],
                className='v-card-content'
            ),
            # OCR output div
            html.Div([
                dcc.Markdown(id='text-output', children='')
            ],
                className="v-card-content")
        ],
        className='app__content'
    )
]
)


@app.callback(Output('text-output', 'children'),
              [Input('canvas', 'json_data')])
def update_data(string):
    if string:
        mask = parse_jsonstring(string, shape=(canvas_height, canvas_width))
        # np.savetxt('data.csv', mask) use this to save the canvas annotations as a numpy array
        print(mask)
        mask = (~mask.astype(bool)).astype(int)
        print(mask)

        # image_string = array_to_data_url((255 * mask[:225]).astype(np.uint8))  # todo: include outputted image as well
        image_string = array_to_data_url((255 * mask).astype(np.uint8))  # todo: include outputted image as well

        # this is from canvas.utils.image_string_to_PILImage(image_string)
        img = Image.open(BytesIO(base64.b64decode(image_string[22:])))  # try save img to see what it looks like?

        img.save("geeks2.png")
        print('img', img)
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
        print('text', text)
        return text  # todo : handle condition which ocr cannot recognize: return message: "enpty, try again"

    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
