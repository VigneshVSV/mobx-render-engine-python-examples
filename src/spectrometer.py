from hololinked.webdashboard.components import (Box, Stack, Button, PlotlyFigure, ButtonGroup, 
                                    RadioGroup, Radio, FormControlLabel)
from hololinked.webdashboard import ReactGridLayout, dataGrid, makeRequest, Cancel
from hololinked.webdashboard.statemachine import RemoteFSM 
import plotly.graph_objects as go




class SpectrometerComponents(Box):

    def __init__(self, id : str, deviceInstanceName : str,  
                serverAddress : str, **params):
        super().__init__(id=id, **params)
        self.deviceInstanceName = deviceInstanceName.replace(r'/','-')
        self.serverAddress = serverAddress 
        self.initGrid()
        self.initControls()
        self.initSpectrumGraph()
        
    def initGrid(self):
        self.grid = ReactGridLayout(
            id=self.deviceInstanceName+"-grid",
            width=1000,
            cols=100,
            rowHeight=1,
            preventCollision=True,
        )
        self.addComponent(self.grid)

    def initControls(self):
        self.processRestartButton = Button(
            id=self.deviceInstanceName + '-restart-spectrometer-process',
            children='Restart',
            color='secondary',
            variant='contained'
        )

        self.processKillButton = Button(
            id=self.deviceInstanceName + '-kill-spectrometer-process',
            children='Kill',
            color='secondary',
            variant='contained'
        )
        
        self.processStartButton = Button(
            id=self.deviceInstanceName + '-start-spectrometer-process',
            children='Start',
            color='secondary',
            variant='contained'
        )

        self.processController = ButtonGroup(
            id=self.deviceInstanceName + '-spectrometer-proces-controller',
            orientation="horizontal",
            color='secondary',
            variant='contained',
            children=[
                self.processRestartButton,
                self.processKillButton,
                self.processStartButton
            ],
            dataGrid=dataGrid(
                x=10,
                y=5,
                w=30,
                h=5
            )
        )
        self.grid.addComponent(self.processController)

        self.startAcquisitionButton = Button(
            id=self.deviceInstanceName + '-spectrometer-start-acquisition',
            children='Start Acquisition',
            variant='outlined',
            sx=dict(
                borderTopRightRadius= 0,
                borderBottomRightRadius=0,
            )
        )
        
        self.stopAcquisitionButton = Button(
            id=self.deviceInstanceName + '-spectrometer-stop-acquisition',
            children='Stop Acquisition',
            variant='outlined',
            sx=dict(
                borderTopLeftRadius= 0,
                borderBottomLeftRadius=0,
            )
        )
     

        # self.acquisitionController = Stack(
        #     id=self.deviceInstanceName + '-spectrometer-acquisition-controller',
        #     direction="row",
        #     children=[
        #         self.startAcquisitionButton,
        #         self.stopAcquisitionButton
        #     ],
        #     dataGrid=dataGrid(
        #         x=40,
        #         y=5,
        #         w=40,
        #         h=5
        #     )
        # )

        # self.grid.addComponent(self.acquisitionController)

        # self.triggerModeControl = RadioGroup(
        #     id=self.deviceInstanceName+'-trigger-mode-controller',
        #     defaultValue='continuous',
        #     dataGrid=dataGrid(
        #         x=40,
        #         y=105,
        #         w=40,
        #         h=5
        #     )
        # )

        # for triggerOption in ['continuous', 'software trigger', 'hardware trigger']:
        #     self.triggerModeControl.addComponent(
        #         FormControlLabel(
        #             id=f"{self.deviceInstanceName}-{triggerOption.replace(r' ', '-')}",
        #             control=Radio(id=f"{self.deviceInstanceName}-{triggerOption.replace(r' ', '-')}-radio"),
        #             checked=True if triggerOption=='continuous' else False,
        #             value=triggerOption,
        #             label=triggerOption
        #         )
        #     )

        # self.acquisitionController.addComponent(self.triggerModeControl)

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
            url = "http://localhost:8082/sentron-pac3200/sim/energy-data",
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