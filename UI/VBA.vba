Sub RunPythonScript()
    Dim pythonPath As String
    Dim scriptPath As String
    Dim cmd As String
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim home As Worksheet
    '---------Parametros------------
    Dim direccionResultados As String
    Dim costoDeOportunidad As String
    Dim cantidadDeClientesPorCamion As String
    Dim cantidadDeCamiones As String
    Dim tonsMaxPorCamion As String
    Dim distMaxPorCliente As String
    
    
    Set wb = ThisWorkbook
    Set home = wb.Worksheet("Home")
    Set direccionResultados = CStr(home.Range("C7").Value)
    Set costoDeOportunidad = CStr(home.Range("C8").Value)
    Set cantidadDeClientesPorCamion = CStr(home.Range("C9").Value)
    Set cantidadDeCamiones = CStr(home.Range("C10").Value)
    Set tonsMaxPorCamion = CStr(home.Range("C11").Value)
    Set distMaxPorCliente = CStr(home.Range("C12").Value)
    
    
    
    '---------GENERO PEDIDOS.CSV------------------
    ' Specify the desired output file path and name
    filePathPedidos = home.Range("C6").Value '--------AGREGAR PATH--------------
    
    ' Specify the worksheet name
    Set ws = wb.Worksheets("Pedidos")
    
    ' Save the worksheet as CSV
    ws.SaveAs Filename:=filePathPedidos, FileFormat:=xlCSV
    
    '----GENERO DISTANCIAS.CSV--------------
    
    ' Specify the desired output file path and name
    filePathDistancias = home.Range("C5").Value '--------AGREGAR PATH--------------
    
    ' Specify the worksheet name
    Set ws = wb.Worksheets("Distancias")
    
    ' Save the worksheet as CSV
    ws.SaveAs Filename:=filePathDistancias, FileFormat:=xlCSV
    
    ' Optional: Close the CSV file without saving changes
    ' ws.Close SaveChanges:=False

    ' Specify the path to your Python executable
    pythonPath = home.Range("C3").Value

    ' Specify the path to your Python script
    scriptPath = home.Range("C4").Value

    ' Construct the command to execute the Python script
    cmd = pythonPath & " " & scriptPath & " " & direccionResultados & " " & costoDeOportunidad & " " & cantidadDeClientesPorCamion & " " & cantidadDeCamiones & " " & tonsMaxPorCamion & " " & distMaxPorCliente

    ' Run the Python script
    Call Shell(cmd, vbNormalFocus)

    ' Continue with the rest of your VBA macro code
    
    
    
End Sub


Sub RunPythonScript()
    Dim pythonPath As String
    Dim scriptPath As String
    Dim cmd As String
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim home As Worksheet
    '---------Parametros------------
    Dim direccionResultados As String
    Dim costoDeOportunidad As String
    Dim cantidadDeClientesPorCamion As String
    Dim cantidadDeCamiones As String
    Dim tonsMaxPorCamion As String
    Dim distMaxPorCliente As String
    Dim range As Range
    
    
    Set wb = ThisWorkbook
    Set home = wb.Worksheet("Home")

    Set range = home.Range("C7")
    direccionResultados = range.Value
    Set range = home.Range("C8")
    costoDeOportunidad = range.Value
    Set range = home.Range("C9")
    cantidadDeClientesPorCamion = range.Value
    Set range = home.Range("C10")
    cantidadDeCamiones = range.Value
    Set range = home.Range("C11")
    tonsMaxPorCamion = range.Value
    Set range = home.Range("C12")
    distMaxPorCliente = range.Value
    
    
    
    '---------GENERO PEDIDOS.CSV------------------
    ' Specify the desired output file path and name
    filePathPedidos = home.Range("C6").Value '--------AGREGAR PATH--------------
    
    ' Specify the worksheet name
    Set ws = wb.Worksheets("Pedidos")
    
    ' Save the worksheet as CSV
    ws.SaveAs Filename:=filePathPedidos, FileFormat:=xlCSV
    
    '----GENERO DISTANCIAS.CSV--------------
    
    ' Specify the desired output file path and name
    filePathDistancias = home.Range("C5").Value '--------AGREGAR PATH--------------
    
    ' Specify the worksheet name
    Set ws = wb.Worksheets("Distancias")
    
    ' Save the worksheet as CSV
    ws.SaveAs Filename:=filePathDistancias, FileFormat:=xlCSV
    
    ' Optional: Close the CSV file without saving changes
    ' ws.Close SaveChanges:=False

    ' Specify the path to your Python executable
    pythonPath = home.Range("C3").Value

    ' Specify the path to your Python script
    scriptPath = home.Range("C4").Value

    ' Construct the command to execute the Python script
    cmd = pythonPath & " " & scriptPath & " " & direccionResultados & " " & costoDeOportunidad & " " & cantidadDeClientesPorCamion & " " & cantidadDeCamiones & " " & tonsMaxPorCamion & " " & distMaxPorCliente

    ' Run the Python script
    Call Shell(cmd, vbNormalFocus)

    ' Continue with the rest of your VBA macro code
    
    
    
End Sub

Sub Pruebas()
    Dim ws As Worksheet
    Dim filePathCell As Range
    Dim filePath As String
    
    Set ws = ThisWorkbook.Worksheets("Home") ' Specify the worksheet name
    Set filePathCell = ws.Range("A1") ' Specify the cell reference
    
    filePath = filePathCell.Value ' Read the value of the cell
    
    MsgBox "The file path is: " & filePath
End Sub

    Set rng = home.Range("C7")
    direccionResultados = rng.Value
    Set rng = home.Range("C8")
    costoDeOportunidad = rng.Value
    Set rng = home.Range("C9")
    cantidadDeClientesPorCamion = rng.Value
    Set rng = home.Range("C10")
    cantidadDeCamiones = rng.Value
    Set rng = home.Range("C11")
    tonsMaxPorCamion = rng.Value
    Set rng = home.Range("C12")
    distMaxPorCliente = rng.Value