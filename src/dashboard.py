from hololinked.server import HTTPServer
from hololinked.webdashboard import ReactApp, Page, ReactGridLayout, RemoteFSM, EventSource, SimpleFSM
from hololinked.webdashboard.components import (Button, TextField, PlotlyFigure, AceEditor,
                                Box, Divider)
from hololinked.webdashboard.axios import makeRequest
from hololinked.webdashboard.components import PlotlyFigure
from hololinked.webdashboard.axios import makeRequest
from hololinked.webdashboard.baseprops import dataGrid 
import plotly.graph_objects as go

from serial_utility import SerialUtility
from spectrometer import SpectrometerComponents



class Dashboard(ReactApp):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.remoteObjects = [
            'https://localhost:8081/serial-communication/system-util',
            'https://localhost:8082/sentron-pac-3200/sim',
            'https://localhost:8083/spectrometer/avantes-avaspec/4096CL'
        ]
        self.initMainPageAndGrid()
        self.initSerialUtil()
        self.initOceanOpticsSpectrometer()
        # self.PACEnergyMeter()
        # self.AvantesSpectrometer()


    def initMainPageAndGrid(self):
        self.mainPage = Page(id = "main-page")
        self.addComponent(self.mainPage)

        self.mainPageGrid = ReactGridLayout(
            id="main-page-grid",
            width=2000,
            cols=400,
            rowHeight=1,
            preventCollision=True
        )
        self.mainPage.addComponent(self.mainPageGrid)


    def initSerialUtil(self):
        self.mainPageGrid.addComponent(
            SerialUtility(
                id='system-serial-utility',
                deviceInstanceName='serial-communication/system-util',
                serverAddress='https://localhost:8081',
                dataGrid=dataGrid(
                    x=0,
                    y=0,
                    w=100,
                    h=40
                )
            )
        )

    def initOceanOpticsSpectrometer(self):
        self.mainPageGrid.addComponent(
            SpectrometerComponents(
                id='ocean-optics-spectrometer',
                deviceInstanceName='spectrometer/ocean-optics/USB2000plus',
                serverAddress='https://localhost:8084',
                dataGrid=dataGrid(
                    x=100,
                    y=0,
                    w=120,
                    h=50
                )
            )
        )

    def PACEnergyMeter(self):
        self.EnergyPlot = go.Figure(
            data = [
                go.Scatter(
                    mode = 'lines+markers',
                    name = 'pyrometer',            
                )],
            layout = go.Layout(
                autosize = True,
                width = 800, 
                height = 800 * (9/16),
                title = "Total Energy Measurement",
                xaxis = dict( title = "time (HH:MM:SS)" ),
                yaxis = dict( title = "Power (W)" ), 
                # grid  = dict( columns = 10, rows = 10)           
            )      
        )

        TotalEnergyPlotSource = makeRequest(
            url = "http://localhost:8082/sentron-pac3200/sim/energy-data",
            method = "get"
        )

        self.TotalEnergyPlotFig = PlotlyFigure(
            id = "sentron-meter-total-energy-plot",
            plot = self.EnergyPlot.to_json(),
            sources = {
                "data[0].x" : TotalEnergyPlotSource.response["returnValue"]["timestamp"],
                "data[0].y" : TotalEnergyPlotSource.response["returnValue"]["total_energy"]
            },
            # stateMachine = RemoteFSM(
            #     subscription = "sentron-pac-3200/sim",
            #     defaultState = 'DISCONNECTED',
            #     MEASURING = dict (
            #         onEntry = TotalEnergyPlotSource,
            #         onExit  = TotalEnergyPlotSource.cancel()
            #     )
            # ),
            dataGrid = dataGrid(
                x = 10,
                y = 32, 
            )
        )
        self.mainPageGrid.addComponent(self.TotalEnergyPlotFig)

        PACConnectButton = Button(
            fullWidth = True, 
            variant = 'contained',
            id = "sentron-pac3200-connect-button",
            dataGrid = dataGrid(
                x = 10,
                y = 75, 
                w = 20
            ),
            # stateMachine = RemoteFSM(
            #     subscription = "sentron-pac-3200/sim",
            #     defaultState = "DISCONNECTED",
            #     DISCONNECTED = dict (
            #         children = "Connect",
            #         color = "primary",
            #         onClick = makeRequest(
            #             url = "http://localhost:8082/sentron-pac3200/sim/connect",
            #             method = "post", 
            #         ),
            #     ),
            #     ON = dict (
            #         children = "sentron-pac-3200/sim",
            #         color = "primary",
            #         onClick = makeRequest( 
            #             url = "http://localhost:8082/sentron-pac3200/sim/disconnect",
            #             method = "post", 
            #         )
            #     ),
            #     MEASURING = dict (
            #         disabled = True,
            #         children = "Disabled (Connect)",
            #     )
            # )
        )
        self.mainPageGrid.addComponent(PACConnectButton)
        
        PACStartAcquisitionButton = Button( 
            fullWidth = True, 
            variant = 'contained',
            id = "sentron-pac3200-acquisition-button",
            dataGrid = dataGrid(
                x = 35,
                y = 75, 
                w = 25
            ),
            color = "primary",
            # stateMachine = RemoteFSM(
            #     subscription = "sentron-pac-3200/sim",
            #     defaultState = "DISCONNECTED",
            #     ON = dict(
            #         children = "Start Acquisition",
            #         onClick = makeRequest(
            #             url = "http://localhost:8082/sentron-pac3200/sim/stop-acquisition",
            #             method = "post", 
            #         ),
            #     ),
            #     MEASURING = dict(
            #         children = "Stop Acquisition",
            #         onClick = makeRequest( 
            #             url = "http://localhost:8082/sentron-pac3200/sim/start-acquisition",
            #             method = "post", 
            #         )
            #     ),
            #     DISCONNECTED = dict (
            #         disabled = True,
            #         children = "Acquisition Disabled",
            #     )
            # )
        )
        self.mainPageGrid.addComponent(PACStartAcquisitionButton)

        self.IndividualMotorEnergyPlot = go.Figure(
            data = [
                go.Scatter(
                    mode = 'lines+markers',
                    name = 'motor 1',            
                ),
                go.Scatter(
                    mode = 'lines+markers',
                    name = 'motor 2',            
                ),
                go.Scatter(
                    mode = 'lines+markers',
                    name = 'motor 3',            
                )],
            layout = go.Layout(
                autosize = True,
                width = 800, 
                height = 800 * (9/16),
                title = "PAC3200 energy meter at individual motors",
                xaxis = dict( title = "time (HH:MM:SS)" ),
                yaxis = dict( title = "Power (W)" ), 
                # grid  = dict( columns = 10, rows = 10)           
            )      
        )

        IndividualMotorsPlotDataSource = EventSource(
            URL = "http://localhost:8082/sentron-pac-3200/sim/event/data-measured",
        )

        StartAcquisitionButton = Button(
            id = "gentec-meter-energy-plot-start-stop-plotting",
            color = 'secondary',
            variant = 'text',
            dataGrid = dataGrid(
                x = 65,
                y = 75
            ),
            # stateMachine = SimpleFSM(
            #     defaultState = 'NOT_PLOTTING', 
            #     NOT_PLOTTING = dict (
            #         children = "Start Plotting",
            #         onClick = IndividualMotorsPlotDataSource, 
            #         target  = 'PLOTTING',
            #         when    = IndividualMotorsPlotDataSource.onConnect
            #     ),
            #     PLOTTING = dict(
            #         children = "Stop Plotting",
            #         onClick = IndividualMotorsPlotDataSource.cancel(), 
            #         target  = 'NOT_PLOTTING', 
            #         when    = IndividualMotorsPlotDataSource.onCancel
            #     )
            # )
        ) 
        self.mainPageGrid.addComponent(StartAcquisitionButton)

        self.IndividualEnergyPlotFig = PlotlyFigure(
            id = "sentron-meter-individual-motor-energy-plot",
            plot = self.IndividualMotorEnergyPlot.to_json(),
            sources = {
                "data[0].x" : IndividualMotorsPlotDataSource.response["timestamp"],
                "data[0].y" : IndividualMotorsPlotDataSource.response["total_energy"]
            },
            dataGrid = dataGrid(
                x = 125,
                y = 32, 
            )
        )
        self.mainPageGrid.addComponent(self.IndividualEnergyPlotFig)
        
    def AvantesSpectrometer(self):
        pass

