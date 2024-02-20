from hololinked.server import HTTPServer
from hololinked.webdashboard import ReactApp, Page, ReactGridLayout, RemoteFSM, EventSource, SimpleFSM
from hololinked.webdashboard.components import (Button, TextField, PlotlyFigure, AceEditor,
                                Box, Divider)
from hololinked.webdashboard.axios import makeRequest
from hololinked.webdashboard.components import PlotlyFigure
from hololinked.webdashboard.axios import makeRequest
from hololinked.webdashboard.baseprops import dataGrid 
import plotly.graph_objects as go


class Dashboard(ReactApp):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


    def initSpectrumGraph(self):
        spectrumPlot = go.Figure(
            data = [
                go.Scatter(
                    mode = 'lines',
                    name = 'Spectrum',            
                )],
            layout = go.Layout(
                autosize = True,
                width = 800, 
                height = 800 * (9/16),
                title = "Spectrum",
                xaxis = dict( title = "Wavelength (nm)" ),
                yaxis = dict( title = "Intensity (Arbitrary Units)" ), 
                # grid  = dict( columns = 10, rows = 10)           
            )      
        )

        spectrumPlotSource = makeRequest(
            url = "http://localhost:8083/",
            method = "get"
        )

        self.spectrumPlotFigure = PlotlyFigure(
            id = self.deviceInstanceName + "-spectrum-plot",
            plot = spectrumPlot.to_json(),
            sources = {
                "data[0].x" : spectrumPlotSource.response["returnValue"]["timestamp"],
                "data[0].y" : spectrumPlotSource.response["returnValue"]["total_energy"]
            },
            stateMachine = RemoteFSM(
                subscription = self.deviceInstanceName,
                defaultState = 'DISCONNECTED',
                MEASURING = dict (
                    onEntry = spectrumPlotSource,
                    onExit  = Cancel(spectrumPlotSource)
                )
            ),
            dataGrid = dataGrid(
                x = 10,
                y = 32, 
                w = 160,
                isDraggable=True
            )
        )
        self.grid.addComponent(self.spectrumPlotFigure)