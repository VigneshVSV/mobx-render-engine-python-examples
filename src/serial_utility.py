from hololinked.webdashboard.components import (Box, TextField, Button, AceEditor,
                                Divider)
from hololinked.webdashboard import (RemoteFSM, dataGrid, AxiosRequestConfig, makeRequests,
                        makeRequest, ReactGridLayout)



class SerialUtility(Box):

    def __init__(self, id : str, deviceInstanceName : str,  
                serverAddress : str, **params):
        super().__init__(id, **params)
        self.deviceInstanceName = deviceInstanceName.replace(r'/', '-')
        self.serverAddress = serverAddress 
        self.initGrid()
        self.initURLInput()
        self.initInstructionInput()
        

    def initGrid(self):
        self.grid = ReactGridLayout(
            id=self.id+"-grid",
            width=500,
            cols=100,
            rowHeight=1,
            preventCollision=True,
        )
        self.addComponent(self.grid)

    def initURLInput(self):
        self.urlTextField = TextField(
            fullWidth = True,
            size = "small",
            label = "Serial URL",
            id = self.id + "-generic-serial-util-serial-url",
            disabled = False,
            dataGrid = dataGrid(
                x = 10,
                y = 5, 
                w = 45,
                h = 0
            ),
            stateMachine = RemoteFSM(
                subscription = self.deviceInstanceName,
                defaultState = "DISCONNECTED", 
                DISCONNECTED = dict (
                    disabled = False
                ),
                ON = dict (
                    disabled = True
                )
            )
        )
        self.grid.addComponent(self.urlTextField)

        COMPORTWrite = AxiosRequestConfig(
            url = f"{self.serverAddress}/{self.deviceInstanceName}/comport",
            method = "put", 
            data = {
                "value" : self.urlTextField.value
            }
        )
        ConnectInvoke = AxiosRequestConfig(
            url = f"{self.serverAddress}/{self.deviceInstanceName}/connect",
            method = "post", 
        )

        self.grid.addComponent(Button(
            fullWidth = True, 
            variant = 'contained',
            id = self.id + "-generic-serial-util-connect-button",
            dataGrid = dataGrid(
                x = 55,
                y = 5, 
                w = 35,
                h = 5
            ),
            size="medium",
            children = "Connect",
            onClick = makeRequests(
                        COMPORTWrite,
                        ConnectInvoke,
                        ignore_failed_requests=False,
                        mode='serial'
                    ),
            stateMachine = RemoteFSM(
                subscription = self.deviceInstanceName,
                defaultState = 'DISCONNECTED',
                DISCONNECTED = dict (
                    children = "Connect",
                ),
                ON = dict (
                    children = "Disconnect",
                    onClick = makeRequest( 
                        url = f"{self.serverAddress}/{self.deviceInstanceName}/disconnect",
                        method = "post", 
                    )
                )
            )
        ))

    def initInstructionInput(self):

        self.instructionTextField = TextField(
            fullWidth = True,
            label = "Instruction",
            size = 'small',
            id = self.id + "-generic-serial-util-instruction-box",
            dataGrid = dataGrid(
                x = 10,
                y = 10, 
                w = 55,
                h = 5
            )
        )
        self.grid.addComponent(self.instructionTextField)

        ExecuteInstruction = makeRequest(
                url = f"{self.serverAddress}/{self.deviceInstanceName}/execute-instruction",
                method = "post", 
                data = {
                    "command" : self.instructionTextField.value,
                    "return_data_size" : 100 
                }
            )
        
        self.instructionSendButton = Button(
            onClick = ExecuteInstruction,
            fullWidth = True, 
            variant = 'contained',
            id = self.id + "-generic-serial-util-send-button",
            children = "Send",
            disabled = True, 
            dataGrid = dataGrid(
                x = 65,
                y = 10, 
                w = 25,
                h = 5,
            ),
            stateMachine = RemoteFSM(
                subscription = self.deviceInstanceName, 
                defaultState = 'DISCONNECTED',
                DISCONNECTED = dict (
                    disabled = True 
                ),
                ON = dict (
                    disabled = False
                )
            )
        )
        self.grid.addComponent(self.instructionSendButton)

        self.instructionReplyEditor = AceEditor(
            readOnly = True,
            # defaultValue = ExecuteInstruction.response,
            fontSize=18,
            showPrintMargin=True,                            
            showGutter=True,
            highlightActiveLine=True,
            wrapEnabled=True,
            placeholder = self.urlTextField.value + " replies appear here",
            minLines = 10,
            id = "generic-serial-util-instruction-reply-editor",
            style={
                "maxHeight" : 200,
                "overflow" : 'auto',
                "scrollBehavior" : 'smooth',
                "width" : "100%",
            }, 
            setOptions={
                "showLineNumbers": True,
                "tabSize" : 4,
                
            }
        )

        replyEditorBox = Box(
            id='generic-serial-util-instruction-reply-box',
            sx=dict(
                border='1px solid grey'
            ),
            dataGrid = dataGrid(
                x = 10,
                y = 15, 
                w = 80,
                h = 20
            ),
        )
        replyEditorBox.addComponent(self.instructionReplyEditor)

        self.grid.addComponent(replyEditorBox)

        self.grid.addComponent(
            Divider(
                id='serial-util-top-border',
                children=['SYSTEM SERIAL UTILITY'],
                dataGrid=dataGrid(
                    x = 10,
                    y = 2, 
                    w = 80,
                    h = 1
                ) 
            ),
            Divider(
                id='serial-util-side-border',
                orientation='vertical',
                dataGrid=dataGrid(
                    x = 92,
                    y = 3, 
                    w = 1,
                    h = 32
                ) 
            )
        )
