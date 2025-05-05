import pandas as pd

# Definir los datos proporcionados
data = [
    [202420899, 'Solorzano Saya Ronald Alex *', 'Transporte', None],
    [202420367, 'Quispe Torres Deissy Lucero', 'Cocina', None],
    [201811324, 'Chata Saavedra Iosef Immanol *', None, None],
    [202420364, 'Larico Iquise Omar Michael *', None, 'Camping'],
    [202420890, 'Chura pacco Edy William *', None, 'Camping'],
    [202420370, 'Tumi Pampa Fernando *', 'Cocina', 'Transporte'],
    [202420884, 'Mamani Challco Yerson Michel', None, None],
    [202420897, 'RUIZ RUPA ANTHONY GABRIEL*', 'Transporte', None],
    [202420504, 'ROJAS VERGARA GABRIEL *', 'Culto', 'Camping'],
    [202420894, 'Estofanero Inofuente Brayan Roy', None, 'Camping'],
    [202414032, 'Chambilla Serrano Juan Diego *', 'Deporte', None],
    [202212960, 'Machaca Condori Brayhan Yobel', 'Actuacion', None],
    [202320618, 'Mamani Pfoccori Luis Omar', None, None],
    [202420366, 'Mestas Gomez Fabricio Fernando *', 'Seguridad', None],
    [202420885, 'Irpanocca Alvarez Johan Emerson *', None, None],
    [202411744, 'Mamani Cahuana Witmer Jhetly', None, 'Transporte'],
    [202420507, 'Calla Ticona Aldo', None, 'Transporte'],
    [202420902, 'Ordoñez Quispe Cristofer Dua', None, None],
    [202411766, 'Ticona Laura Gema Nikol', None, None],
    [202420887, 'Torres Arias Anghelo Hernan', None, 'Camping'],
    [202420891, 'Calsin Mamani Kengui Pieri', 'Botiquin', None],
    [202420883, 'SANCHEZ SARAVIA JOAQUIN HASSAN', 'Actuacion', 'Transporte'],
    [202414037, 'Berrios Flores Abel Yeins', None, 'Transporte'],
    [202420901, 'Larico Quispe Nelson Antony', 'Deporte', 'Seguridad'],
    [202420888, 'Cabana Cruz Edgar D Alessandro', 'Canto', None],
    [202411747, 'Ramos Ancco Alexander', None, 'Camping'],
    [202420882, 'Yupanqui Tolentino Yesmi Karol', None, 'Camping'],
    [202420361, 'Araujo Puma Rodrigo', None, None],
    [202420886, 'Chambilla Chambilla Hermes Adan', 'Culto', 'Canta'],
    [202420506, 'Quispe Tito Juan Daniel', 'Culto', 'Seguridad'],
    [202420880, 'Bilbao Lizarraga Andre Fabricio', None, 'Transporte/Seguridad'],
    [202420362, 'Perez Mamani Fiorella Del Carmen', None, None],
    [202420903, 'Choque Velarde Jhosepmir Henry', None, None],
    [202420363, 'Quispe Oquendo Zamyr Nelio', None, None],
    [202312743, 'Blanco Huacasi Yenyfer', None, None],
    [202420369, 'QUISPE BELLIDO JOSE FERNANDO', None, None],
    [202320600, 'Soncco Cruz Fidel Edison', 'Seguridad', None]
]

# Crear un DataFrame
df = pd.DataFrame(data, columns=["Codigo", "Nombre", "Lideres", "Ayudantes"])

# Separar las comisiones y los que no tienen comisiones
comisiones = df[(df['Lideres'].notnull()) | (df['Ayudantes'].notnull())]
sin_comisiones = df[df['Lideres'].isnull() & df['Ayudantes'].isnull()]

# Crear un archivo Excel con dos hojas
with pd.ExcelWriter("comisiones_y_sin_comisiones.xlsx") as writer:
    comisiones.to_excel(writer, sheet_name="Comisiones", index=False)
    sin_comisiones.to_excel(writer, sheet_name="Sin Comisiones", index=False)
