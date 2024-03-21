from flask import Flask, render_template, request
import random
import qrcode
from captcha import validar_captcha

app = Flask(__name__)

class CURPGenerator:
    @staticmethod
    def generar_primer_digito(fecha_nacimiento):
        anio = int(fecha_nacimiento[:4])
        if anio <= 1999:
            return str(random.randint(0,0))
        else:
            return random.choice('A')

    @staticmethod
    def calcular_digito_verificador(curp_sin_verificador):
        caracteres_validos = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
        equivalencias = {char: index for index, char in enumerate(caracteres_validos)}
        coeficientes = [18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        suma = sum(coef * equivalencias[char] for coef, char in zip(coeficientes, curp_sin_verificador))
        residuo = suma % 10
        if residuo == 0:
            return '0'
        else:
            return str(10 - residuo)

def calcular_homoclave(apellido_paterno, apellido_materno, nombre, fecha_nacimiento, sexo):
    curp_gen = CURPGenerator()
    return curp_gen.generar_primer_digito(fecha_nacimiento)

def generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado):
    curp = ''
    rfc = ''
    curp += apellido_paterno[0].upper()
    for letra in apellido_paterno[1:]:
        if letra.upper() in 'AEIOU':
            curp += letra.upper()
            break
    curp += apellido_materno[0]
    curp += nombre[0]
    curp += fecha_nacimiento[2:4]
    curp += fecha_nacimiento[5:7]
    curp += fecha_nacimiento[8:10]
    curp += sexo
    curp += estado
    for letra in apellido_paterno[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break
    for letra in apellido_materno[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break
    for letra in nombre[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break
    homoclave = calcular_homoclave(apellido_paterno, apellido_materno, nombre, fecha_nacimiento, sexo)
    curp += homoclave
    digito_verificador = CURPGenerator.calcular_digito_verificador(curp)
    curp += digito_verificador

    rfc += apellido_paterno[:2].upper()
    rfc += apellido_materno[:1].upper()
    rfc += nombre[:1].upper()
    rfc += fecha_nacimiento[2:4]
    rfc += fecha_nacimiento[5:7]
    rfc += fecha_nacimiento[8:10]
    rfc += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    rfc += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    return curp, rfc

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/generar_curp', methods=['POST'])
def generar_y_mostrar_curp():
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    fecha_nacimiento = request.form['fecha_nacimiento']
    sexo = request.form['sexo']
    estado = request.form['estado']
    captcha = request.form['captcha']

    if not validar_captcha(captcha):
        return render_template('error.html', error="Captcha incorrecto. Inténtalo de nuevo.")

    curp_generada, rfc_generado = generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado)
    qr_content = f'CURP: {curp_generada}\nRFC: {rfc_generado}'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_file = f"static/Qrs/{curp_generada}.png"
    img.save(img_file)

    return render_template('formulario.html', curp=curp_generada, rfc=rfc_generado, img_file=img_file)

if __name__ == '__main__':
    app.run(debug=True)
